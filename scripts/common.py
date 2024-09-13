import re

import boto3
import paramiko


def execute_command(
    ip_address: str, key_path: str, command: str, username: str = "ubuntu"
) -> str:
    """Execute a command against a remote machine.

    Returns:
        stdout of command from remote machine if command successes

    Raises:
        RunTime error if command not successful on remote machine
    """
    # Set up SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the instance
        ssh_client.connect(
            hostname=ip_address, username=username, key_filename=key_path
        )

        # Execute the command and collect output
        stdin, stdout, stderr = ssh_client.exec_command(command)
        stdout_str = stdout.read().decode()
        stderr_str = stderr.read().decode()

        # Close the connection
        ssh_client.close()

    except Exception as e:
        print(f"Error connecting to {ip_address}: {str(e)}")
        raise e

    if stderr_str:
        print(stderr_str)
        raise RuntimeError(f"Command '{command}' failed on '{ip_address}'")

    return stdout_str


def extract_join_command(text: str) -> str:
    """Extracts docker swarm join command from text"""
    match = re.search(
        r"docker swarm join --token [\w-]+ \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+",
        text,
    )
    if not match:
        raise ValueError(f"Could not extract swarm join command from text: '{text}'")
    return match.group(0)


def ec2_ips_by_name(aws_profile: str, name: str) -> list[str]:
    """Return list of IP address of EC2 instances filtered by name"""
    print(f"Using AWS profile '{aws_profile}'.")
    print(f"Looking for EC2 instances with tag 'Name={name}'.")

    # Set up boto3 session and EC2 resource
    session = boto3.Session(profile_name=aws_profile)
    ec2_resource = session.resource("ec2")

    # Get a list of all running EC2 instances with the specified name tag
    instances = ec2_resource.instances.filter(
        Filters=[
            {"Name": "instance-state-name", "Values": ["running"]},
            {"Name": "tag:Name", "Values": [name]},
        ]
    )

    # Get the IP addresses of all the instances
    ip_addresses = [instance.public_ip_address for instance in instances]
    print(f"Collected {len(ip_addresses)} IP addresses: {ip_addresses}")
    return ip_addresses
