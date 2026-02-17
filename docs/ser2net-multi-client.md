# Using ser2net for Multiple Client Access

## Overview

By default, a serial device (e.g., `/dev/ttyUSB0`) can only be accessed by one application at a time. If you want to use both the Home Assistant THZ integration and the FHEM THZ module simultaneously with the same heat pump, you'll need a solution that allows multiple clients to connect.

**ser2net** is a serial port gateway that makes serial devices accessible over TCP/IP networks. It can act as a bridge, allowing multiple clients to connect to the same serial device over the network. This enables both Home Assistant and FHEM to communicate with your THZ heat pump at the same time.

### How It Works

```
┌─────────────────┐
│  THZ Heat Pump  │
│  (Serial Port)  │
└────────┬────────┘
         │
         │ USB/Serial
         │
┌────────▼────────┐
│    ser2net      │
│  (TCP Server)   │
└────────┬────────┘
         │
         ├─────────► Home Assistant (TCP client)
         │
         └─────────► FHEM (TCP client)
```

The ser2net daemon:
1. Opens the physical serial connection to your heat pump
2. Listens on a TCP port (e.g., 2323)
3. Forwards data between the serial port and multiple TCP clients

## Important Warnings

⚠️ **Protocol Collision Risks**: When multiple clients connect to the same serial device through ser2net, there's a risk of **protocol collision**. This occurs when:

- Both Home Assistant and FHEM send requests to the heat pump simultaneously
- Responses from the heat pump get mixed up or delivered to the wrong client
- Commands from different clients interleave, causing protocol errors

**Potential Issues:**
- Corrupted or incorrect sensor readings
- Failed write operations
- Unpredictable behavior in both systems
- Connection timeouts or errors

**Risk Mitigation:**
- Use **read-only mode** in one of the systems when possible
- Configure different polling intervals to minimize collision probability
- Use longer polling intervals (e.g., 60+ seconds) to reduce traffic
- Monitor logs for protocol errors and connection issues
- Consider using only one system for write operations (control)

⚠️ **This is an unsupported configuration**: While ser2net enables multi-client access, the THZ protocol was not designed for concurrent access. Use at your own risk and be prepared to troubleshoot issues.

## ser2net Installation

### Installing on Debian/Ubuntu/Raspberry Pi OS

```bash
sudo apt-get update
sudo apt-get install ser2net
```

### Installing on Other Linux Distributions

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install ser2net
# or on older systems:
sudo yum install ser2net
```

**Arch Linux:**
```bash
sudo pacman -S ser2net
```

### Checking ser2net Version

Different versions of ser2net use different configuration formats and have different multi-client capabilities:

```bash
ser2net -v
```

- **Version 3.5 or newer**: Uses YAML configuration, **supports multiple simultaneous client connections** via `max-connections` option (RECOMMENDED for multi-client use)
- **Version 3.4 or older**: Uses legacy text-based configuration, **typically limited to ONE client connection at a time** with the `raw` state

⚠️ **For simultaneous Home Assistant + FHEM access, ser2net 3.5+ is strongly recommended.**

## Configuration Examples

### Modern ser2net (3.5+) YAML Configuration

For ser2net version 3.5 and newer, create or edit `/etc/ser2net/ser2net.yaml`:

```yaml
%YAML 1.1
---
# ser2net configuration for THZ heat pump
# Allows multiple clients (Home Assistant + FHEM) to access serial device

connection: &thz
  accepter: tcp,2323
  enable: on
  options:
    kickolduser: true
  connector: serialdev,/dev/ttyUSB0,115200n81,local
  timeout: 0
```

**Configuration breakdown:**
- `accepter: tcp,2323` - Listen on TCP port 2323
- `enable: on` - Enable this connection
- `kickolduser: true` - Disconnect old connection when new one arrives (allows reconnection)
- `connector: serialdev,/dev/ttyUSB0,115200n81,local` - Serial device configuration
  - `/dev/ttyUSB0` - Serial device path (adjust as needed)
  - `115200n81` - Baudrate 115200, 8 data bits, no parity, 1 stop bit
  - `local` - Ignore modem control lines
- `timeout: 0` - No timeout, keep connections alive

**Note**: Modern ser2net (3.5+) supports multiple simultaneous connections by default. The `kickolduser: true` option allows reconnection but doesn't limit to single client. For explicit multi-client control, you can add additional options (consult ser2net 3.5+ documentation for advanced settings).

**Important**: Adjust `/dev/ttyUSB0` to match your actual device. Find it with:
```bash
ls -l /dev/ttyUSB* /dev/ttyACM*
```

### Legacy ser2net (3.4 and older) Configuration

⚠️ **Important Limitation**: Legacy ser2net versions (3.4 and older) with the `raw` state typically **only allow ONE client connection at a time**. For true simultaneous multi-client access (Home Assistant + FHEM), you should upgrade to **ser2net 3.5 or newer** which supports the YAML configuration format with `max-connections` option.

If you're using legacy ser2net, the configuration below will work, but only one client can connect at a time. When a second client attempts to connect, it will typically be rejected or the first connection may be dropped depending on your ser2net version.

For older ser2net versions, edit `/etc/ser2net.conf`:

```conf
# ser2net.conf - Configuration for THZ heat pump
#
# Format: <network-port>:<state>:<timeout>:<device>:<options>
#
# LIMITATION: In legacy ser2net (3.4-), the 'raw' state typically allows
# only ONE client connection at a time. For multiple simultaneous clients,
# upgrade to ser2net 3.5+ with YAML configuration.
#
# network-port: TCP port to listen on
# state: raw, rawlp, telnet, off
# timeout: timeout in seconds (0 = no timeout)
# device: serial device path
# options: serial parameters and options

# THZ Heat Pump connection
# Port 2323, raw mode, no timeout, 115200 baud 8N1
2323:raw:0:/dev/ttyUSB0:115200 8DATABITS 1STOPBIT NONE LOCAL
```

**Configuration breakdown:**
- `2323` - TCP port to listen on
- `raw` - Raw TCP mode (no telnet protocol processing) - **allows only 1 client in legacy versions**
- `0` - No timeout (keep connections alive indefinitely)
- `/dev/ttyUSB0` - Serial device path (adjust as needed)
- `115200` - Baudrate (must match heat pump: 115200)
- `8DATABITS 1STOPBIT NONE` - Serial parameters (8N1)
- `LOCAL` - Ignore modem control lines (DCD, DTR)

**Workarounds for legacy ser2net:**

If you cannot upgrade to ser2net 3.5+, consider these alternatives:

1. **Use time-based switching**: Configure Home Assistant and FHEM to access the heat pump at different times (never simultaneously)
2. **Upgrade ser2net**: The recommended solution - upgrade to ser2net 3.5 or newer for true multi-client support
3. **Use two serial ports**: If your heat pump has multiple serial interfaces, connect separate USB adapters
4. **Choose one system**: Use either Home Assistant OR FHEM, not both simultaneously

### Starting and Enabling ser2net

After configuring ser2net:

```bash
# Check configuration syntax
sudo ser2net -c /etc/ser2net.conf -n  # For legacy version
sudo ser2net -c /etc/ser2net/ser2net.yaml -n  # For YAML version

# Start the service
sudo systemctl start ser2net

# Enable automatic start on boot
sudo systemctl enable ser2net

# Check service status
sudo systemctl status ser2net

# View logs
sudo journalctl -u ser2net -f
```

## Home Assistant Configuration

The Home Assistant THZ integration already supports TCP connections through the `connection="ip"` mode, which is designed to work with ser2net.

### Configuration Steps

1. Navigate to **Settings** → **Devices & Services** in Home Assistant
2. Click **"+ ADD INTEGRATION"**
3. Search for **"Stiebel Eltron LWZ / Tecalor THZ Integration"**
4. In the configuration wizard:
   - **Connection Type**: Select **"Network (ser.net)"**
   - **Host**: Enter the IP address of the machine running ser2net
     - If ser2net runs on the same machine as Home Assistant: use `localhost` or `127.0.0.1`
     - If ser2net runs on a different machine: use that machine's IP address (e.g., `192.168.1.100`)
   - **Port**: Enter the TCP port ser2net is listening on (default: `2323`)
5. Complete the setup

### Technical Details

The Home Assistant integration uses TCP keepalive to maintain stable connections:
- Keepalive probes start after 60 seconds of inactivity
- Probes are sent every 10 seconds
- Connection closes after 6 failed probes

This is implemented in `thz_device.py` and ensures the connection remains stable even during long periods between polling cycles.

### Recommended Polling Settings

To minimize protocol collisions when using multiple clients:
- Use **longer polling intervals** (e.g., 60-120 seconds) instead of the default
- Configure polling intervals in the integration options if available
- Monitor the logs for any communication errors

## FHEM Configuration

To configure FHEM to use the ser2net connection:

### FHEM Configuration Example

Add or modify your THZ device definition in FHEM:

```perl
# Using ser2net TCP connection instead of direct serial
define myTHZ THZ 192.168.1.100:2323

# If ser2net is on the same machine as FHEM:
define myTHZ THZ localhost:2323

# Set polling interval (seconds) - use longer intervals for multi-client
attr myTHZ poll_interval 90

# Optional: Set to readonly mode to avoid write conflicts
# attr myTHZ readonly 1
```

**Configuration parameters:**
- `192.168.1.100:2323` - ser2net host IP and port
- `poll_interval 90` - Poll every 90 seconds (adjust as needed)
- `readonly 1` - Optional: disable write operations in FHEM

### FHEM Polling Recommendations

- Set `poll_interval` to 90-120 seconds or higher
- Offset FHEM and Home Assistant polling times if possible
- Consider using FHEM in read-only mode if you primarily control via Home Assistant

## Best Practices

### 1. Connection Management

- **Don't restart both clients simultaneously** - Stagger restarts by 30-60 seconds
- **Monitor connection status** in both systems
- **Use TCP keepalive** to maintain stable connections (HA does this automatically)

### 2. Polling Strategy

- **Use long polling intervals**: 60-120 seconds minimum for each client
- **Offset polling times**: If HA polls at :00 seconds, set FHEM to poll at :30 seconds
- **Avoid aggressive polling**: More frequent polling increases collision risk
- **Monitor for errors**: Check logs regularly for protocol errors

### 3. Write Operations

- **Designate one system for control**: Use one system for write operations (changing settings)
- **Use read-only mode**: Configure one system in read-only mode when possible
- **Test carefully**: Test any write operations and verify they succeed
- **Avoid simultaneous writes**: Never change settings in both systems at the same time

### 4. Reliability

- **Run ser2net on dedicated hardware**: Ideally run ser2net on a stable, always-on system
- **Use a reliable USB-serial adapter**: Choose quality USB-serial adapters for stability
- **Monitor ser2net logs**: Check `journalctl -u ser2net` regularly
- **Plan for failures**: Have a recovery procedure if ser2net crashes

### 5. Security

- **Firewall protection**: If ser2net is network-accessible, restrict access to trusted IPs
- **Local-only access**: When possible, run all components on the same machine
- **No encryption**: ser2net doesn't encrypt data - avoid exposing it on untrusted networks

## Limitations

### ser2net Version Limitations

1. **Legacy ser2net (3.4 and older)**: The `raw` state typically allows **only ONE client connection at a time**. True multi-client support requires ser2net 3.5+
2. **Upgrade required**: For simultaneous Home Assistant + FHEM access, upgrading to ser2net 3.5+ is essential

### Protocol-Level Limitations

1. **No request coordination**: Clients don't know about each other's requests
2. **Response confusion**: Responses may be delivered to the wrong client
3. **Collision potential**: Simultaneous requests can corrupt the protocol
4. **No locking mechanism**: The heat pump has no multi-client support

### Technical Limitations

1. **No guaranteed delivery**: Lost responses are not retried
2. **No transaction support**: Partial writes cannot be rolled back
3. **Timing sensitive**: Protocol timing depends on both clients being "well-behaved"
4. **Debugging difficulty**: Multi-client issues are hard to diagnose

### Practical Limitations

1. **Reduced reliability**: More points of failure than single-client setup
2. **Complex troubleshooting**: Issues may be intermittent or timing-dependent
3. **Limited support**: This is not an officially supported configuration
4. **Performance impact**: Multiple clients increase serial bus traffic

## Troubleshooting

### ser2net Not Starting

**Problem**: ser2net service fails to start

**Solutions**:
```bash
# Check configuration syntax
sudo ser2net -c /etc/ser2net.conf -d -d

# Check if serial device exists and has correct permissions
ls -l /dev/ttyUSB0
sudo usermod -a -G dialout ser2net

# Check service logs
sudo journalctl -u ser2net -n 50

# Check if another process is using the serial port
sudo lsof /dev/ttyUSB0
```

### Connection Refused

**Problem**: Home Assistant or FHEM cannot connect to ser2net

**Solutions**:
```bash
# Verify ser2net is listening
sudo netstat -tlnp | grep 2323
sudo ss -tlnp | grep 2323

# Test connection manually
telnet localhost 2323
nc -v localhost 2323

# Check firewall rules (if connecting from another machine)
sudo iptables -L -n | grep 2323
sudo ufw status
```

### Second Client Cannot Connect (Legacy ser2net)

**Problem**: When using ser2net 3.4 or older, the second client (either Home Assistant or FHEM) cannot connect, or connecting the second client disconnects the first one.

**Cause**: Legacy ser2net (version 3.4 and older) with the `raw` state typically allows only **ONE client connection at a time**. This is a fundamental limitation of the legacy configuration format.

**Solutions**:

1. **Upgrade to ser2net 3.5 or newer** (RECOMMENDED):
   ```bash
   # Check current version
   ser2net -v
   
   # Upgrade on Debian/Ubuntu/Raspberry Pi OS
   sudo apt-get update
   sudo apt-get upgrade ser2net
   
   # After upgrading, convert to YAML configuration
   # See the "Modern ser2net (3.5+) YAML Configuration" section above
   ```

2. **Use time-based switching** (workaround):
   - Configure Home Assistant to access the heat pump during certain hours
   - Configure FHEM to access during different hours
   - Never run both simultaneously

3. **Choose one system** (simplest):
   - Migrate fully to either Home Assistant or FHEM
   - Most reliable solution if ser2net upgrade is not possible

4. **Verify you're actually on legacy ser2net**:
   ```bash
   # Check version - if 3.5+, use YAML config instead
   ser2net -v
   
   # If using 3.5+, check for YAML config file
   ls -l /etc/ser2net/ser2net.yaml
   ```

### Timeout Errors

**Problem**: Frequent timeout errors in Home Assistant or FHEM

**Possible causes**:
- Protocol collisions from simultaneous requests (if using ser2net 3.5+ with multi-client)
- ser2net connection timeout set too low
- Serial device instability
- USB-serial adapter issues

**Solutions**:
1. **Increase polling intervals** in both clients
2. **Verify ser2net timeout** is set to 0 (no timeout)
3. **Check USB connection**: Try a different USB port or cable
4. **Monitor ser2net logs**: `sudo journalctl -u ser2net -f`
5. **Restart ser2net**: `sudo systemctl restart ser2net`

### Incorrect or Corrupted Data

**Problem**: Sensors show wrong values or change unexpectedly

**Possible causes**:
- Protocol collisions between clients
- Both clients writing simultaneously
- Response delivered to wrong client

**Solutions**:
1. **Increase polling intervals** to reduce collision probability
2. **Set one client to read-only mode**
3. **Verify only one client writes** at a time
4. **Check logs** in both Home Assistant and FHEM for errors
5. **Consider using only one client** for critical operations

### Device Disconnects

**Problem**: Clients frequently disconnect from ser2net

**Solutions**:
```bash
# Check TCP keepalive is enabled (HA does this automatically)
# For FHEM, you may need to configure keepalive in FHEM

# Check ser2net is stable
sudo systemctl status ser2net

# Increase ser2net buffer sizes (in config file if needed)

# Check system resources
top
free -h
df -h
```

### ser2net Crashes

**Problem**: ser2net service crashes or stops unexpectedly

**Solutions**:
```bash
# Check system logs
sudo journalctl -u ser2net -n 200

# Check for segfaults or crashes
sudo dmesg | grep ser2net

# Update to latest ser2net version
sudo apt-get update && sudo apt-get upgrade ser2net

# Enable automatic restart on failure
sudo systemctl edit ser2net
```

Add to override file:
```ini
[Service]
Restart=always
RestartSec=10
```

### Testing Your Setup

To verify everything is working:

1. **Test ser2net connectivity**:
   ```bash
   # Should show TCP connection established
   telnet localhost 2323
   ```

2. **Monitor ser2net logs** during connection:
   ```bash
   sudo journalctl -u ser2net -f
   ```

3. **Check Home Assistant logs** for THZ integration errors

4. **Check FHEM logs** for THZ device errors

5. **Monitor sensor values** in both systems - they should be consistent

6. **Test a write operation** from one client while monitoring the other

## Alternative Approaches

If ser2net multi-client access proves unreliable, consider these alternatives:

### 1. Use Only One System
- Migrate fully to either Home Assistant or FHEM
- Simplest and most reliable solution
- No protocol collision risks

### 2. Time-Based Access
- Configure one system to access during certain hours
- Use cron jobs or automations to enable/disable integrations
- Guaranteed no simultaneous access

### 3. Read-Only Secondary Access
- Use Home Assistant for full control (read/write)
- Use FHEM only for reading values (read-only mode)
- Reduces but doesn't eliminate collision risk

### 4. Separate Hardware
- Use two separate USB-serial adapters if your heat pump supports it
- Some systems have multiple serial ports
- Check your heat pump documentation

## References

- [ser2net Project](https://github.com/cminyard/ser2net)
- [Home Assistant THZ Integration](https://github.com/bigbadoooff/thz)
- [FHEM THZ Module](https://wiki.fhem.de/wiki/THZ)
- [ser2net Documentation](http://ser2net.sourceforge.net/)

## Getting Help

If you encounter issues not covered in this guide:

1. **Check the logs** from ser2net, Home Assistant, and FHEM
2. **Search for similar issues** in the GitHub issues
3. **Open an issue** with detailed information:
   - ser2net version and configuration
   - Home Assistant version and THZ integration version
   - FHEM version and THZ module version
   - Error messages from all three systems
   - Polling intervals configured in both clients
   - Whether write operations are being performed

Remember: Multi-client access through ser2net is not officially supported and may have inherent limitations. Be prepared to fall back to single-client access if issues cannot be resolved.
