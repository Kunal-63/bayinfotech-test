---
kb_id: KB-004
title: Virtual Lab Environment Management
version: 1.0
tags: [virtual-lab, environment, containers, virtual-machines]
category: Lab Operations
---

# Virtual Lab Environment Management

## What is a Virtual Lab?

A virtual lab is a containerized or virtualized environment where you can safely practice cybersecurity tasks without affecting production systems.

### Lab Types

- **Isolated Labs**: Standalone environments with no external access
- **Connected Labs**: Can communicate with other lab environments
- **Production-like Labs**: Mirror production architecture for realistic training
- **Sandbox Labs**: Allow experimentation without permanent consequences

## Lab Access

### Starting a Lab

1. Go to Dashboard
2. Find the desired lab module
3. Click "Start Lab"
4. Wait for environment to initialize (1-5 minutes)
5. Click "Launch" to access lab environment

### Lab Resources

Each lab includes:
- Virtual machines or containers
- Isolated network segments
- Pre-configured services and applications
- Sample data and test files
- Logging and monitoring tools

## Lab Environment Components

### Virtual Machines

Each lab may include multiple VMs:

- **Linux Machines**: Ubuntu, CentOS, Alpine
- **Windows Machines**: Windows Server, Windows 10
- **Specialized Machines**: Firewalls, DNS servers, web servers

### Networking

Labs have isolated networks:

- **Subnet**: 10.x.x.0/24
- **Gateway**: 10.x.x.1
- **DHCP**: Enabled by default
- **NAT**: Access to internet (configurable)

### Storage

- **Root Volume**: 40GB (Linux) or 80GB (Windows)
- **Data Volume**: 100GB (shared across lab)
- **Snapshot**: Automatic backup when lab starts

## Common Lab Tasks

### Access Virtual Machine

1. Click VM in lab console
2. VNC/RDP window opens
3. Log in with provided credentials
4. Use terminal or desktop interface

### Reset VM

1. Right-click VM name
2. Select "Reset VM"
3. Confirm action
4. VM reboots and resets to initial state

### Check Network Connectivity

From within lab:
```
ping 8.8.8.8          # Test internet
ping 10.x.x.x         # Test lab network
nslookup google.com   # Test DNS
```

### View Logs

1. Click "Logs" tab in lab
2. Select VM or service from dropdown
3. View real-time logs
4. Download logs for analysis

## Lab Limitations

### Resource Constraints

- **CPU**: Limited to 4 cores per lab
- **Memory**: Limited to 8GB per lab
- **Storage**: 100GB data volume
- **Bandwidth**: 10Mbps (simulated)

### Time Limits

- **Active Lab**: 4 hours maximum
- **Paused Lab**: 24 hours maximum
- **Auto-shutdown**: After max time, lab terminates

### Behavioral Limits

- Cannot access host system
- Cannot modify lab network infrastructure
- Cannot access other users' labs
- Cannot perform certain dangerous operations (kernel module loading, etc.)

## Saving Lab Work

### Checkpoints

Create checkpoints to save progress:

1. Click "Create Checkpoint"
2. Give checkpoint a name
3. Lab pauses and saves state
4. Continue or restore from checkpoint later

### Exporting Data

To save files from lab:

1. Click "Export" button
2. Select files to export
3. Exported files downloaded to your computer
4. Keep for reference or submission

## Lab Completion

### Ending a Lab

1. Complete all tasks
2. Click "End Lab"
3. Confirm termination
4. Lab environment deleted
5. Work saved via checkpoint or export

### Lab Report

After lab:
- View lab report with your actions and results
- Download certificate (if applicable)
- Review score and feedback
- Access lab recordings (if enabled)

## Lab Best Practices

- Read lab instructions fully before starting
- Save progress with checkpoints frequently
- Test configurations before committing
- Document your actions and findings
- Export important work before lab ends
- Ask support if lab components fail

## Troubleshooting Lab Issues

### Lab Won't Start

- Check system requirements
- Clear browser cache
- Try different browser
- Wait a few minutes and retry
- Contact support if persists

### Connection Issues

- Check internet connection
- Verify firewall allows lab connections
- Try resetting lab connection
- Check lab firewall rules
- Contact support

### Performance Issues

- Close unnecessary applications
- Check system resources (CPU, RAM)
- Reduce number of running VMs
- Disable unnecessary services in lab
- Contact support for VM issues
