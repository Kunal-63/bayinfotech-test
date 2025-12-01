---
kb_id: KB-002
title: Network Troubleshooting Guide
version: 1.0
tags: [networking, troubleshooting, diagnostics, connectivity]
category: Troubleshooting
---

# Network Troubleshooting Guide

## Common Network Issues

This guide helps you diagnose and resolve common network connectivity problems.

## Checking Network Status

To check if your network is working:

1. Open terminal or command prompt
2. Run: `ping 8.8.8.8` (Google's public DNS)
3. If you get responses, your internet connection is working
4. If timeout, check your WiFi or ethernet connection

## WiFi Connection Problems

### WiFi Won't Connect

1. Check if WiFi is enabled on your device
2. Look for your network in available networks list
3. Enter the correct password
4. If still not connecting:
   - Restart your router (turn off for 10 seconds, then on)
   - Check if other devices can connect
   - Move closer to the router

### Slow WiFi Speed

- Move closer to the router
- Check for interference from microwaves or cordless phones
- Reduce number of connected devices
- Update router firmware
- Switch to 5GHz band if available

## DNS Problems

DNS issues prevent you from accessing websites by name.

### Check DNS

Run: `nslookup google.com` (Windows/Mac) or `dig google.com` (Linux)

### Fix DNS

If DNS is not working:

1. Windows: 
   - Go to Network Settings
   - Change DNS to 8.8.8.8 and 8.8.4.4 (Google DNS)

2. Mac/Linux:
   - Edit `/etc/resolv.conf`
   - Add: `nameserver 8.8.8.8`

3. Router:
   - Access router admin panel (usually 192.168.1.1)
   - Update DNS settings
   - Save and restart

## Ethernet Connection Issues

### No Ethernet Connection

1. Check if cable is properly connected on both ends
2. Inspect cable for damage (kinks, cuts, burns)
3. Try a different ethernet cable
4. Try a different ethernet port on your device
5. Update network drivers

### Intermittent Connection

- Check cable connections
- Try a shorter ethernet cable
- Update network drivers
- Check switch/hub ports
- Replace network card if available

## Port Accessibility

To check if a specific port is accessible:

- Windows: `Test-NetConnection -ComputerName hostname -Port 8080`
- Linux/Mac: `nc -zv hostname 8080` or `telnet hostname 8080`

## Firewall Configuration

If port is not accessible, firewall may be blocking it.

### Windows Firewall

1. Open Windows Defender Firewall with Advanced Security
2. Click "Inbound Rules"
3. Click "New Rule"
4. Select "Port"
5. Choose TCP or UDP
6. Enter port number
7. Allow the connection

### Linux (iptables)

```
# Allow port
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo iptables -A OUTPUT -p tcp --sport 8080 -j ACCEPT

# Save rules
sudo service iptables save
```

## When to Escalate

Contact support if:
- All basic troubleshooting fails
- Multiple ports are inaccessible
- Network is unstable across all devices
- Hardware appears damaged
- You cannot modify firewall settings
