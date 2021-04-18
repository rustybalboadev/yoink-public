<div align="center">
    <h1><a href="https://yoink.rip">yoink.rip</a></h1>
</div>

# Description
yoink.rip is a flask application I made early October of 2020 that focuses on being a remake of [grabify](https://grabify.link) with more realistic domains.

# Installation:

First clone the repository by running the following command:
```
git clone https://github.com/RustyBalboadev/yoink-public.git
```
Now you will need to install the modules required to run the app
```
pip install -r requirements.txt
```
The next step will be filling out the config file named ``config.yaml``
| Config Required Fields |
|------------------------|
| mongo-uri              |
| secret-key             |
| base-url               |
| encryption-key         |

Now to run the flask application run
```
flask run
```
and the app will be running on [localhost:5000](http://localhost:5000)