<h1 align="center">
	<img
		width="300"
		alt="BEYOND logo with planet as the O"
		src="media/BEYOND%20Light%20Mode.png"
  >
</h1>

<h3 align="center">
	Backend repository for the BEYOND space catalog web application
</h3>

## Setup
You will need to have terraform installed on your machine and an AWS account.

Replace the user ID in this line in `main.tf` with your AWS user ID: `"Resource": "arn:aws:dynamodb:ca-central-1:455720929055:table/beyond-users"`

Navigate to the `/infra` folder and initialize terraform with `terraform init`. 
Use `terraform plan` to see what changes will be made, and `terraform apply` to apply the changes. 


## File Structure
- `/infra` contains our terraform file to create and manage resources.
- `/functions` contains our AWS lambda functions code. 
