# K3s Ansible Deployment

Declarative K3s management for single-node cluster.

## Structure

```
k3s-ansible/
├── inventory/
│   └── hosts.ini          # Server inventory
├── group_vars/
│   └── all.yml            # K3s version and config
├── playbooks/
│   └── k3s-master.yml     # Main playbook
└── roles/
    └── k3s/
        └── tasks/
            └── main.yml   # K3s installation tasks
```

## Quick Start

### 1. Initial Installation

```bash
ansible-playbook -i inventory/hosts.ini playbooks/k3s-master.yml
```

### 2. Upgrade K3s

Update version in `group_vars/all.yml`:

```yaml
k3s_version: v1.35.0+k3s1
```

Run playbook:

```bash
ansible-playbook -i inventory/hosts.ini playbooks/k3s-master.yml
```

## Configuration

### group_vars/all.yml

- `k3s_version`: Target K3s version
- `k3s_snapshot_before_upgrade`: Auto-snapshot before upgrade
- `k3s_do_drain`: Drain node before upgrade (false for single-node)
- `k3s_snapshot_retention`: Number of snapshots to keep

## Features

- Automatic etcd snapshots before upgrade
- Version comparison and conditional upgrade
- Kernel module configuration
- Sysctl parameters for Kubernetes
- Kubeconfig download to local machine
- Snapshot retention management
- K3s configuration via `/etc/rancher/k3s/config.yaml` (declarative)
- Uses k3s default network CIDRs (cluster: 10.42.0.0/16, service: 10.43.0.0/16)

## Manual Operations

### View snapshots

```bash
ssh root@ip 'ls -lh /var/lib/rancher/k3s/server/db/snapshots/'
```

### Restore snapshot

```bash
ssh root@ip 'k3s server --cluster-reset --cluster-reset-restore-path=/var/lib/rancher/k3s/server/db/snapshots/SNAPSHOT_NAME'
```

### Check K3s status

```bash
ssh root@ip 'systemctl status k3s'
```

ansible-playbook -i inventory/hosts.ini playbooks/k3s-master.yml

ansible-playbook -i inventory/hosts.ini playbooks/k3s-master.yml --check --diff

ansible-playbook -i inventory/hosts.ini playbooks/configure-additional-ip.yml

cat /etc/netplan/*.yaml