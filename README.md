# README - iCare Odoo 17 & PostgreSQL Setup

This project provides a setup for running Odoo 17 with PostgreSQL 15 using Docker Compose. The configuration is managed via the `docker-compose.yml` file.

## Prerequisites

Make sure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Project Structure

- `docker-compose.yml`: Defines services for Odoo and PostgreSQL.
- `postgresql/`: Directory to store PostgreSQL data.
- `z_addons/`: Directory for custom Odoo addons.
- `logs/`: Directory for Odoo logs.
- `config/`: Configuration files for Odoo.
- `entrypoint.sh`: Custom entrypoint for the Odoo container.

## How to Use

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://zen8labs@dev.azure.com/zen8labs/iCare/_git/iCare
cd iCare
```

### 2. Prepare the Environment

Ensure you have the necessary files and directories:

- `docker-compose.yml`: This script is used as the entry point for the Odoo container. You may want to adjust it based on your needs
- Create empty directories for postgresql, z_addons, logs, and config:
```bash
mkdir postgresql z_addons logs config
```

### 3.  Modify Configuration (Optional)

You can adjust the following parameters in the `docker-compose.yml` file:
- `PostgreSQL`:
  - POSTGRES_USER: Odoo database user (default: odoo)
  - POSTGRES_PASSWORD: Password for Odoo database user (default: odoo16@2022)
  - POSTGRES_DB: Default database to be created (default: postgres)
- `Odoo`: 
  - HOST: PostgreSQL service name (default: icare_db)
  - USER: Odoo database user (default: odoo)
  - PASSWORD: Password for Odoo database user (default: odoo16@2022)

### 4. Run the Project

Start the containers by running:
```bash
docker-compose up -d
```
### 5. Access Odoo

Once the containers are running, you can access the Odoo application by navigating to:
- Odoo web interface: http://localhost:8069
- Live chat interface: http://localhost:8072

### 6. Logs and Debugging

- Odoo logs are saved in the ./logs directory.
- PostgreSQL data is saved in the ./postgresql directory.

To view logs for a specific service, you can use:
```bash
docker-compose logs <service-name>
```

### 7. Stopping the Containers
To stop the containers, run:
```bash
docker-compose down
```










