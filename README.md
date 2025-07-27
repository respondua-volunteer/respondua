## Respondua – Volunteer Project

Welcome to **Respondua**, a volunteer-driven project created to support communities through accessible technology, collaboration, and compassion.

## 🫶 About the Project

**Respondua** is part of the **Vidguk Foundation**, a charitable initiative born in response to the war in Ukraine.  
Since February 24, 2022, we’ve been united by one goal — **to help those in need**.

This website was built by volunteers to connect people with vital resources, support, and each other.  
It is open-source and built with ❤️ by contributors from all around the world.

We believe in fast, transparent, and human-centered digital tools for real-world impact.

## Tech Stack

- **Backend**: Django (Python)
- **Frontend**: HTML/CSS/JS
- **Database**: PostgreSQL
- **Containerization**: Docker
- **Hosting**: AWS EC2 + Nginx + SSL

## Getting Started

```bash
git clone https://github.com/respondua/respondua.git
cd respondua
docker-compose up
```

## Contributing
We welcome contributions!
If you'd like to help with development, design, translation, or community outreach — check out our [CONTRIBUTING](./CONTRIBUTING.md)

## License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.


sudo docker-compose -f docker-compose.yaml up --build -d

docker exec -it volunteer python manage.py migrate

git tag -a v0.2.5 -m "my version v0.2.5"

git push origin v0.2.4

scp -o StrictHostKeyChecking=no -r init-letsencrypt.sh ubuntu@IP:/home/ubuntu/app

VIRT env

source venv/Scripts/activate usefull commands for django
python manage.py runserver
python manage.py migrate
python manage.py makemigrations
python manage.py createsuperuser
python manage.py collectstatic


python manage.py compilemessages --ignore=env

python manage.py loaddata app/fixtures/authors.json

python manage.py dumpdata > db.json

netstat -an | grep 0.0.0.0:5432 tcp 0 0 0.0.0.0:5432 0.0.0.0:* LISTEN

ssh -N ubuntu@3.69.216.243 -L 1111:0.0.0.0:5432