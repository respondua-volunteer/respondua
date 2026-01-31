# PostgreSQL Backup & Restore

## Автоматические бэкапы

Бэкапы запускаются автоматически по расписанию через CronJob.

### Настройки

```yaml
backup:
  enabled: true
  schedule: "0 2 * * *"          # Каждый день в 2 ночи
  retentionDays: 7               # Хранить 7 дней
  persistence:
    size: 20Gi                   # Размер хранилища
```

## Просмотр бэкапов

```bash
# Создать временный под для просмотра бэкапов
kubectl run -n postgresql postgres-backup-shell --rm -it \
  --image=bitnamilegacy/postgresql:17.6.0-debian-12-r4 \
  --overrides='
{
  "spec": {
    "containers": [{
      "name": "postgres-backup-shell",
      "image": "bitnamilegacy/postgresql:17.6.0-debian-12-r4",
      "command": ["/bin/bash"],
      "stdin": true,
      "tty": true,
      "volumeMounts": [{
        "name": "backup-storage",
        "mountPath": "/backups"
      }]
    }],
    "volumes": [{
      "name": "backup-storage",
      "persistentVolumeClaim": {
        "claimName": "postgresql-backup-pvc"
      }
    }]
  }
}' \
  -- bash

# В открывшейся оболочке:
ls -lh /backups
```

## Ручной запуск бэкапа

```bash
# Создать Job из CronJob
kubectl create job -n postgresql postgresql-backup-manual \
  --from=cronjob/postgresql-backup

# Проверить статус
kubectl get jobs -n postgresql
kubectl logs -n postgresql job/postgresql-backup-manual
```

## Восстановление из бэкапа

### Вариант 1: Через временный под

```bash
# 1. Создать под с доступом к бэкапам и PostgreSQL
kubectl run -n postgresql postgres-restore-shell --rm -it \
  --image=bitnamilegacy/postgresql:17.6.0-debian-12-r4 \
  --env="POSTGRES_PASSWORD=$(kubectl get secret -n postgresql postgresql-secrets -o jsonpath='{.data.POSTGRES_ADMIN_PASSWORD}' | base64 -d)" \
  --overrides='
{
  "spec": {
    "containers": [{
      "name": "postgres-restore-shell",
      "image": "bitnamilegacy/postgresql:17.6.0-debian-12-r4",
      "command": ["/bin/bash"],
      "stdin": true,
      "tty": true,
      "env": [{
        "name": "POSTGRES_PASSWORD",
        "valueFrom": {
          "secretKeyRef": {
            "name": "postgresql-secrets",
            "key": "POSTGRES_ADMIN_PASSWORD"
          }
        }
      }],
      "volumeMounts": [{
        "name": "backup-storage",
        "mountPath": "/backups"
      }]
    }],
    "volumes": [{
      "name": "backup-storage",
      "persistentVolumeClaim": {
        "claimName": "postgresql-backup-pvc"
      }
    }]
  }
}' \
  -- bash

# 2. В открывшейся оболочке:
# Просмотреть доступные бэкапы
ls -lh /backups

# Восстановить из конкретного бэкапа
gunzip < /backups/postgresql_backup_20251208_143530.sql.gz | psql -h postgresql -U postgres

# Или восстановить конкретную базу
gunzip < /backups/postgresql_backup_20251208_143530.sql.gz | psql -h postgresql -U postgres -d your_database
```

### Вариант 2: Через kubectl exec

```bash
# 1. Скопировать бэкап из backup PVC в локальную директорию
kubectl run -n postgresql backup-copy --rm --restart=Never \
  --image=bitnamilegacy/postgresql:17.6.0-debian-12-r4 \
  --overrides='
{
  "spec": {
    "containers": [{
      "name": "backup-copy",
      "image": "bitnamilegacy/postgresql:17.6.0-debian-12-r4",
      "command": ["sleep", "3600"],
      "volumeMounts": [{
        "name": "backup-storage",
        "mountPath": "/backups"
      }]
    }],
    "volumes": [{
      "name": "backup-storage",
      "persistentVolumeClaim": {
        "claimName": "postgresql-backup-pvc"
      }
    }]
  }
}'

# 2. Скопировать бэкап локально
kubectl cp postgresql/backup-copy:/backups/postgresql_backup_20251208_143530.sql.gz ./backup.sql.gz

# 3. Скопировать в PostgreSQL под
kubectl cp ./backup.sql.gz postgresql/postgresql-0:/tmp/backup.sql.gz

# 4. Восстановить
kubectl exec -n postgresql postgresql-0 -- bash -c \
  "gunzip < /tmp/backup.sql.gz | PGPASSWORD=\$POSTGRES_PASSWORD psql -U postgres"

# 5. Удалить временный под
kubectl delete pod -n postgresql backup-copy
```

## Мониторинг бэкапов

```bash
# Проверить статус последних бэкапов
kubectl get jobs -n postgresql -l component=backup

# Логи последнего бэкапа
kubectl logs -n postgresql -l component=backup --tail=100

# История CronJob
kubectl get cronjobs -n postgresql
kubectl describe cronjob -n postgresql postgresql-backup
```

## Тестирование бэкапа

```bash
# Создать тестовую базу
kubectl exec -n postgresql postgresql-0 -- psql -U postgres -c "CREATE DATABASE test_backup;"
kubectl exec -n postgresql postgresql-0 -- psql -U postgres -d test_backup -c "CREATE TABLE test (id INT, name TEXT);"
kubectl exec -n postgresql postgresql-0 -- psql -U postgres -d test_backup -c "INSERT INTO test VALUES (1, 'before backup');"

# Запустить бэкап
kubectl create job -n postgresql test-backup --from=cronjob/postgresql-backup

# Дождаться завершения
kubectl wait --for=condition=complete --timeout=300s job/test-backup -n postgresql

# Изменить данные
kubectl exec -n postgresql postgresql-0 -- psql -U postgres -d test_backup -c "INSERT INTO test VALUES (2, 'after backup');"
kubectl exec -n postgresql postgresql-0 -- psql -U postgres -d test_backup -c "SELECT * FROM test;"

# Восстановить из бэкапа (см. инструкции выше)

# Проверить данные (должна быть только запись "before backup")
kubectl exec -n postgresql postgresql-0 -- psql -U postgres -d test_backup -c "SELECT * FROM test;"

# Очистить
kubectl delete job -n postgresql test-backup
kubectl exec -n postgresql postgresql-0 -- psql -U postgres -c "DROP DATABASE test_backup;"
```

## Troubleshooting

### Бэкап не создается

```bash
# Проверить логи CronJob
kubectl logs -n postgresql -l component=backup --tail=100

# Проверить права доступа к PVC
kubectl exec -n postgresql postgresql-backup-XXXXX -- ls -la /backups

# Проверить доступ к PostgreSQL
kubectl exec -n postgresql postgresql-backup-XXXXX -- pg_isready -h postgresql
```

### Недостаточно места для бэкапов

```bash
# Проверить использование PVC
kubectl exec -n postgresql <backup-pod> -- df -h /backups

# Увеличить размер PVC в values.yaml
backup:
  persistence:
    size: 50Gi  # Увеличить размер

# Или уменьшить retention period
backup:
  retentionDays: 3  # Хранить меньше дней
```

### Восстановление не работает

```bash
# Проверить, что бэкап файл не поврежден
kubectl run -n postgresql check-backup --rm -it \
  --image=bitnamilegacy/postgresql:17.6.0-debian-12-r4 \
  --overrides='{"spec":{"containers":[{"name":"check","image":"bitnamilegacy/postgresql:17.6.0-debian-12-r4","command":["gunzip","-t","/backups/postgresql_backup_20251208_143530.sql.gz"],"volumeMounts":[{"name":"backup-storage","mountPath":"/backups"}]}],"volumes":[{"name":"backup-storage","persistentVolumeClaim":{"claimName":"postgresql-backup-pvc"}}]}}'

# Если ошибка "gzip: invalid compressed data", бэкап поврежден
```
