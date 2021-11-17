# nouns-automations
Nouns automations is a project built for [NounsDAO](https://nouns.wtf/) to allow building automations using Zapier and Integromat.
This repo hosts the server side that serves the data to Zapier & Integromat. Visit our public [Notion page](https://verbs.notion.site/Nouns-Automations-using-Integromat-Zapier-7f3af840dc1d4a04b1d728f978c785b0) for more context. 

# How to contribute
Feel free to open issues/pull requests.

# Using the automations
* Zapier: https://zapier.com/developer/public-invite/145904/8a8e34e04debec63de5fef1526fe3879/
* Integromat: https://www.integromat.com/en/apps/invite/6b5f6756542eb1dc5aac97ff95cf2e68

# Live implementations
* [Nouns Google Calendar](https://verbs.notion.site/Nouns-Google-Calendar-c8314d548aed4aa1b841cb868b9ea0a8)
* [NounsCalendar Twitter Bot](https://verbs.notion.site/NounsCalendar-Twitter-Bot-5821b01f5df24e91bf9dbace931ecd8c)

# Running locally
1. Clone the repo
2. `pipenv install && pipenv shell`
3. Create a new mysql database locally
4. Create a `.envrc` file based on `.envrc.example`. `.envrc` uses [direnv](https://direnv.net/), you can use any other method to set env variables.
   1. Set the `DJANGO_SECRET_KEY`
   2. Set the mysql connection details
   3. Set the alchemy api key
5. Create database tables: `python manage.py migrate`
6. Run the server: `python manage.py runserver`
   1. Go to `http://127.0.0.1:8000/auctions/` to see if everything works
7. Schedule background job to check for new auctions:
   1. `python manage.py schedule_check_for_new_auctions`
8. To run the background jobs, in a new shell, inside `pipenv shell` run: `python manage.py qcluster`
