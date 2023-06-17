<!-- ABOUT THE PROJECT -->

## Erganiser

![Django][Django-img] ![Postgres][Postgres-img] ![Python][Python-img] ![macOs]
![Linux] ![Docker]

![Pytest] ![Black]


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about">About</a>
      <ul>
        <li><a href="#features">Features</a></li>
        <li><a href="#faq">FAQ</a></li>
      </ul>
    </li>
    <li><a href="#development">Development</a></li>
        <ul>
        <li><a href="#dependencies">Dependencies</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#using-docker">Using Docker</a></li>
        <li><a href="#Contributing-and-supporting-Ergansier">Contributing 
and supporting Ergansier</a></li>
        </ul>
    </li>
  </ol>
</details>

<!-- About -->
## About

**Erganiser is a small web application which allows athletes and their coaches
to log, monitor and compare their erg scores in a safe and anonymous way.**

In rowing, erg scores are a good indicator of an athlete's fitness and can
be the deciding factor in selection for a crew. However, erg scores are
sensitive information and can be a source of anxiety for athletes. This is
especially true for younger athletes who are still developing and may not
be able to perform at their best yet. Whilst comparing scores with other
athletes can be a good motivator, it can also lead to stress and shame.
Erganiser tries to keep the positive aspects of comparing scores whilst
minimalising the negative ones, by allowing athletes to compare their scores
within their squad in an anonymous way.
Only coaches can see the names of their athletes, and their respective scores.

<!-- Features -->
### Features

- Log your erg scores
- Compare your scores anonymously within your squad
- Syncronise your scores from your concept2 logbook

<!-- FAQ -->
### FAQ

#### I want to sync my concept2 logbook scores but get an oauth error

- This might be related to an issue with the refresh token from the
  oauth service concept2 uses to authorize your account. Try to go into
  your profile settings, ensure that your logbook id is correct and
  delete the stored api key and try it again. If that doesn't help please
  feel free to drop me a message.

#### Can I sync my scores from my concept2 logbook automatically?

- This is a feature I would like to implement in the future. However, I
  would like to make sure that the user has full control over when and
  how their data is synced.

#### Why can't I sync my scores from the rp3 app?

- I would absolutely love to be able to implement a feature which allows to
  sync the scores from the rp3 app. However, the rp3 app does not provide an
  open API to access the data.

#### I have a feature request or found a bug

- Please feel free to open an issue on github or drop me a message.

<!-- Development -->

## Development

**If you want to contribute to the code base or just want to run the service
yourself, please read on.**

<!-- Dependencies -->

### Dependencies

**This code is developed and tested to be deployed on macOS or Linux. It is
not tested on Windows. I recommend using the <a href="#using-docker">
Installation with Docker</a> for Windows users.**

- Python Version 3.9
- Django Version 4.1
- Psycopg2 2.9.5
- Python-dateutil 2.8.2
- Django-crispy-forms 1.14.0
- Django-ses 3.4.1
- Django-tempus-dominus 5.1.2.17
- Django-Verify-Email 2.0.3
- Python-dateutil 2.8.2
- Python-dotenv 1.0.0

To install all dependencies navigate into the project folder and run:

   ```sh
   pip install -r requirements.txt
   ```

<!-- Installation -->

### Installation

1. Clone the repo
   ```sh
   git clone git@github.com:Slange-Mhath/Erganiser.git
   ```

2. Navigate into the project directory
   ```sh
   cd Erganiser
   ```

3. Set the environment variables
   ```sh
   export SECRET_KEY=YOUR_DJANGO_SECRET_KEY
   ```
   ```sh
   export C2_CLIENT_ID=YOUR_C2_CLIENT_ID
   ```
   ```sh
   export C2_CLIENT_SECRET=YOUR_C2_CLIENT_SECRET
   ```
   ```sh
   export AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID
   ```
   ```sh
   export AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
   ```
   or alternatively create a .env file in the root directory and add the
   required variables there.

4. Create a superuser by following the prompts after entering the following
   command
    ```sh
   python3 manage.py createsuperuser
   ```

5. start the server
   ```sh
   python3 manage.py runserver   
   ```
<!-- Using Docker -->
### Using Docker

If you want to run this service in a Docker Container, no problem at all!

1. Clone the repo
   ```sh
   git clone git@github.com:Slange-Mhath/Erganiser.git

2. Navigate into the project directory
   ```sh
   cd Erganiser
   ```
3. Build the Docker image
   ```sh
    docker build -t erganiser .
    ```
4. Create .env file in Erganiser root folder and add the following env 
   variables:
   - SECRET_KEY
   - C2_CLIENT_ID
   - C2_CLIENT_SECRET
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   

5. Run Docker Compose to start Postgres and Webserver
   ```sh
   docker-compose up -d 
   ```
5. Create a superuser by following the prompts after entering the following
   command
    ```sh
   docker-compose exec web python manage.py createsuperuser
   ```
<!-- Contributing and supporting Ergansier -->
### Contributing and supporting Ergansier

If you want to contribute to the project, that's great! You can do so by 
one of the following ways:

- [Open an Issue and tell me about your suggestions and ideas](https://github.com/Slange-Mhath/Erganiser/issues)
- [Clone the repo and open a pull request](https://github.com/Slange-Mhath/Erganiser/pulls)
- [Support the project by donating to the Falcon Boat Club](https://wonderful.org/pay?ref=1186921)

[Django-img]: https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white

[Python-img]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54

[macOS]: https://img.shields.io/badge/mac%20os-000000?style=for-the-badge&logo=macos&logoColor=F0F0F0

[Linux]: https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black

[Docker]:https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white

[Black]: https://img.shields.io/badge/code%20style-black-000000.svg

[Pytest]: https://img.shields.io/badge/Pytest-passing-sucess

[Postgres-img]: https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white


