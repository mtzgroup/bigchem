"""Start a Docker Swarm on AWS.

Pass this script three arguments:
    1. The AWS credentials profiles to use. If you only have one profile use 'default'.
        This the profile created by running "aws configure" from the command line.
        https://aws.amazon.com/cli/
    2. The name you gave the machines when you deployed them. This can also be a tag
        you added with key "Name" and then the value you set
    3. Path to the .pem file needed to SSH into the instances

Example:
    python scripts/swarm_aws.py default bigchem ~/.ssh/aws-key.pem
"""
from common import ec2_ips_by_name, execute_command, extract_join_command

if __name__ == "__main__":
    import sys

    aws_profile = sys.argv[1]
    ec2_name_tag = sys.argv[2]
    key_path = sys.argv[3]

    # Collect IP addresses of EC2 instances with Name=ec2_name_tag
    ip_addresses = ec2_ips_by_name(aws_profile, ec2_name_tag)

    for i, addr in enumerate(ip_addresses):
        if i == 0:
            # Make first IP address the manager node
            print(f"Making Manager node: {addr}")
            stdout = execute_command(addr, key_path, "docker swarm init")
            swarm_join_command = extract_join_command(stdout)

        else:
            # Make all other nodes workers
            print(f"Making Worker node: {addr}")
            stdout = execute_command(addr, key_path, swarm_join_command)
            print(stdout)

    if ip_addresses:
        # If nodes were found
        print(
            f"SSH in to your Manager node at {ip_addresses[0]} to start services or "
            "stacks on your swarm"
        )
