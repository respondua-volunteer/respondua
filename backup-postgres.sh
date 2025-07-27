#!/bin/bash

name="postgres-backup"
date=$(date +%Y-%m-%d"_"%H_%M_%S)
s3_location="s3://postgres-backup-respond"
backup_filename="${name}_${date}.sql.gz"

docker exec -i postgres /usr/bin/pg_dump \
 -U postgres postgres | gzip -9 > $backup_filename

#upload to s3
aws s3 cp $backup_filename $s3_location

rm $backup_filename

echo "Backup to s3 $backup_filename done"