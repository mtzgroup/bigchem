"""Add worker nodes to Docker Swarm on AWS.

Pass this script three arguments:
    1. The AWS credentials profiles to use. If you only have one profile use 'default'.
        This the profile created by running "aws configure" from the command line.
        https://aws.amazon.com/cli/
    2. The name you gave the machines when you deployed them. This can also be a tag
        you added with key "Name" and then the value you set
    3. Path to the .pem file needed to SSH into the instances
    4. The IP address of the Manager node

Example:
    python scripts/swarm_aws.py default bigchem ~/.ssh/aws-key.pem 53.168.56.102
"""
from common import ec2_ips_by_name, execute_command, extract_join_command

if __name__ == "__main__":
    import sys

    aws_profile = sys.argv[1]
    ec2_name_tag = sys.argv[2]
    key_path = sys.argv[3]
    manager_ip_address = sys.argv[4]

    ip_addresses = ec2_ips_by_name(aws_profile, ec2_name_tag)

    # Get Swarm Join command from Manager
    print("Collecting swarm join command from Manager...")
    stdout = execute_command(
        manager_ip_address, key_path, "docker swarm join-token worker"
    )
    swarm_join_command = extract_join_command(stdout)
    print("Success!")

    for i, addr in enumerate(ip_addresses):
        # Add nodes as worker
        print(f"Making Worker node: {addr}")
        stdout = execute_command(addr, key_path, swarm_join_command)
        print(stdout)
