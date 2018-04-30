
![](https://github.com/hasadna/kikar-hamedina/blob/dev/kikar_hamedina/static/media/kikar_hamedina_logo.png)

[![Build Status](https://travis-ci.org/hasadna/kikar-hamedina.svg?branch=master)](https://travis-ci.org/hasadna/kikar-hamedina)

# Welcome to Kikar Hamdina #

Welcome to Kikar Hamedina, An Open-Source Project by The Public Knowledge Workshop.
 
We monitor Israeli MKs' activity in the Social Media, and put it in context.

You can see our live website at [kikar.org](http://www.kikar.org).


#### Are a developer who's looking to get involved? ####
Great! take a look at our [GitHub Issues](https://github.com/hasadna/kikar-hamedina/issues). In particular, 
anything labeled as **MiniBites** is a great place to startp with. We'd love your help!

Please read below for project set-up instructions, and contribution guidelines.


#### Are you interested in helping out, but not by coding? ####
No worries, We might still have something for you. You are invited to 
<a href="mailto:yotammanor@gmail.com?subject='I Want to Help with Kikar Hamedina'">contact us</a>, and we'll find you a place.

## Setting Up The Project ##

### Prerequisites ###

* GitHub Account (and preferably some git knowledge).
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
* [Vagrant](https://www.vagrantup.com/downloads.html)
* A personal Test Facebook App (see below for [details](#fb-app-instruction))
* An IDE is highly recommended. PyCharm is a good example.

### Installation ###

* Fork this project to your GitHub account.
* Clone your fork of the project into your local repository.
* Add the original repository, so you can pull changes in: `git remote add hasadna https://github.com/hasadna/kikar-hamedina/`
* Using your favorite command-line, go to the project's directory (defaults to kikar-hamedina)
* Run `cp kikar_hamedina/kikar_hamedina/local_settings.py.template kikar_hamedina/kikar_hamedina/local_settings.py`
* Open **local_settings.py**, and edit the following parameters:

  1. SECRET_KEY - a random string of characters of your choice.
  2. FACEBOOK_SECRET_KEY - from your facebook app. [see below](#fb-app-instruction).
  3. FACEBOOK_APP_ID  - from your facebook app. [see below](#fb-app-instruction).

* Run `vagrant plugin install vagrant-vbguest`


* **Before you go up**: If you want to run the server to a different port (rather than 8000), you can add an 
**environment variable** like this: `export KIKAR_HAMEDINA_PORT=1234` (Linux/Mac),  or `set KIKAR_HAMEDINA_PORT=1234` (Windows).  

* Run `vagrant up`. First time might take a while. this can take about 25-30 minutes. If you are running on a windows machine please make sure you have virutalization enabled, which is something you need to do on your BIOS.

* If you reached a point where the output talks about creating and updating statuses, you're good to go!

* You can now access the server from your browser on http://localhost:8000/ (or your chosen port)

* You can also run `vagrant ssh` to go inside your virtual machine. The Django project will be 
at `../../vagrant/kikar_hamedina`.

* See [here](#vagrant-instructions) for instructions on how to use vagrant

#### Setting-up a Facebook App <a name="fb-app-instruction"></a> ####

* Go to **[Facebook Developers](https://developers.facebook.com/)**
* On the upper left menu, select **"My apps"** and there select **"Create a new app"**.
* In the dialog opened, choose **Website**.
* On upper-right, choose **"skip and create app id"**.
* Choose a *name**, and a **category** (I usually put news, but it's bot important). Then click **"Create App ID"**
* Now you'll see a **dashboard**, with **APP ID** and a **SECRET KEY**.
* **Important**: You also want your **app website** to be defined as: **http://localhost:8000/** (or the address:port you'll
 be using). This can be done at the **Settings** Menu.


## Working On Our Code ##

### Code Contribution Guidelines ###
 
 * **Task management** is done here on GitHub. Keep the **issues** list tidy, assign yourself to task you take, and unassign as needed..
 * New features should be branched from `dev`. Branch name should be the issues number e.g. `270`. 
 * Commits should meet the [following guidelines](https://chris.beams.io/posts/git-commit/).
 * In order to incorporate your code in `dev`, create a **pull request**. Please keep in mind that **Your Code will be reviewed. So write it well**.
 * Our current testing framework is somewhat off (and the [issue](https://github.com/hasadna/kikar-hamedina/issues/275) that deals with it is aching for an assignee!). Until this issue is handled, manual testing is extra necessary.
 * Branch `master` is our production branch, and should always be downstream from `dev`. Never commit directly to it, it won't be accepted in.
 

### Using Vagrant <a name="vagrant-instructions"></a> ###

Here's a handy list of vagrant commands maintenance:

* `vagrant up` - create virtual machine or run it if it is down

* `vagrant halt` - stop a virtual machine, without destroying it

* `vagrant destroy` - destroy virtual machine

* `vagrant reload` - a short for halt and then up.

* `vagrant provision` - run all the scripts to that predefine the machine (sets up ubuntu, python, postgres, django, etc.)

* `vagrant reload --provision` - halt, up, provision.

* `vagrant global-status` - see status of all machines

* `vagrant ssh [<id>]`  - ssh into machine


### Navigating within the VM <a name="vagrant-instructions"></a>###

After SSH'ing into the machine, you can use it as if it's your very own linux machine.

Here are some project specific commands you want to know:
* **See the server log** in /var/log/upstart/kikar.log (e.g. ``sudo tail -F /var/log/upstart/kikar.log``)
* `cd ../../vagrant/kikar_hamedina` will bring you to the location of `manage.py`.

These commands can be used to manage the django server (these are standard Upstart commands):

* `sudo stop kikar`

* `sudo start kikar`

* `sudo restart kikar`

* `sudo status kikar`


### Troubleshooting ###
1. Windows only - Make sure you have ssh installed, and can run ssh through CMD, a good way to do that is using git	testing: https://help.github.com/articles/testing-your-ssh-connection/
	If not, OpenSSH :)
2. Make sure CPU supports virtualization - google "Enable Virtualization Technology"
3. Vagrant GUI is pretty helpful with troubleshooting, todo so uncomment the gui proerty from the VagrantFile

# Other Stuff #
####Editing data_fixture####

At the main directory there's a sub-directory called data. Within it there are four csv files, 
for Party, Person, Feed, and Tag data, which can be edited.

* Note that in order to handle encoding correctly those csv files are UTF-8, which Microsoft Excel does not create as
 default. You may reffer to http://stackoverflow.com/questions/4221176/excel-to-csv-with-utf8-encoding for help.

Once you're done editing, create the json file by running ``data_fixture_helper_script_csv_to_json.py``, and replace 
the old data_fixture_facebook_feeds.json with the new one.

Another option would be to edit data with the django Admin, and then run:
``python manage.py dumpdata core.Party core.Person core.Facebook_Feed core.Tag --indent 4 > <file_name>.json``

A script to convert the json to the csv files exists as well. Note that currently the file names are hardcoded, 
so use with caution..
