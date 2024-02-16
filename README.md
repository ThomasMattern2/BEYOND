# BEYOND

To provide users with information regarding space such as stars, planets, nebulae, galaxies, etc. Allow users to input newly discovered sky objects to add to the database. Users can look up groups of objects based on date, constellation, magnitude, etc. This repository contains the backend code of our project.

Group Members:
- Alessandro Baldassarre
- Rita Boury
- Feranmi Falade
- Chantae Ho
- Isaac Hus
- Thomas Mattern 
- Carson May

## Setup
You will need to have terraform installed on your machine and an AWS account.

Replace the user ID in this line in `main.tf` with your AWS user ID: `"Resource": "arn:aws:dynamodb:ca-central-1:455720929055:table/beyond-users"`

Navigate to the `/infra` folder and initialize terraform with `terraform init`. 
Use `terraform plan` to see what changes will be made, and `terraform apply` to apply the changes. 


## File Structure
- `/infra` contains our terraform file to create and manage resources.
- `/functions` contains our AWS lambda functions code. 
