# Proctor!

## User Guide

## Welcome
<i>Procto</i>r is a Python 3.6 command-line application that enables you to grade Java-based projects. 
It is intended for use by Wentworth Institute of Technology (WIT) instructors. This document serves 
as a user guide and as a reference.

The application runs on various operating systems including Windows, Linux and MacOS, and relies 
on having network access to a GitLab server. 

It has been tested on the following:
* MacOS Mojave 10.15
* <B>OTHERS HERE</B>.

Note that Proctor is inspired heavily by Derbinsy's witgrade, offering increased simplicity at the 
cost of fewer features.

## What Can I Do with Proctor?
Proctor enables you to perform the following actions:
* Verify access to a GitLab server
* Clone Java projects from a GitLab server to your local machine
* Grade Java projects that you've cloned
* Manage groups on a GitLab server

Before we dive into how to do these things, let's set up our environment and get a 
copy of the application up and running.


## Setting up Your Enviroment
Before you can run Proctor, you need a working environment. Specifically, you need 
the following SDKs and associated runtimes installed on your computer:

* Java 8 or higher. All references to Java hereafter assume 8 or higher.
* JUnit 4.x. The application was tested with JUnit 4.12. 
* Git
* Python 3.6 or higher. All references to Python hereafter assume 3.6 or higher.


Note that you have two choices relative to using Proctor:
* You can set up the required tech stack yourself
* You can download and use a preconfigured Docker image. 

The following directions explain how to set up a local environment. If you'd
rather use the Docker image, you can skip to that section.

### Download, Install and Configure Java & JUnit
Because Proctor is designed to help grade Java and JUnit-based projects, you need to have
the Java SDK installed, as well as a copy of JUnit. Proctor will use the tools installed
with the JDK and JUnit to build and test projects.

* [Java JDK Download](https://www.oracle.com/technetwork/java/javase/downloads/index.html)
* [JUnit 4.x Download](https://junit.org/junit4/)

Download and install the Java JDK and JUnit framework, and configure them normally. There is 
nothing special you need to do with these to make Proctor work.

### Set Up Git
Use the most recent version of Git.

* [Download Git](https://git-scm.com/downloads)
* Install & configure Git


### Set Up Python & Python Virtual Environment
Python virtual environments are isolated sandboxes for Python distributions and projects.
Each virtual environment is a complelety separate installation of Python, enabling you to have 
multiple copies and versions of Python running on your machine at the same time. 
Each project can maintain its own set of modules, dependencies, etc.

There are several tools that enable you to manage virtual environments including <i>virtualenv</i> and
<i>miniconda</i>. I prefer miniconda, and subsequent directions are miniconda-relative. That said, 
you should use the tool with which you're most comfortable or familiar. You can read about each 
and download your favorite from the following links:

* [virtualenv](https://virtualenv.pypa.io/en/latest/)
* [miniconda](https://docs.conda.io/en/latest/miniconda.html)

If you choose miniconda, it ships with Python (version 3.7 at the time of this writing) and installs it 
as part of the overall installation process. If you choose another virtual environment manager, 
you may need to [download Python](https://www.python.org/downloads/) first, in a separate 
installation step. 

#### Install Virtual Environment Manager
* Download & install the virtual environment manager of choice.

#### Create New Virtual Environment
* From a terminal window, create a virtual environment based on Python 3.6 or above. 
You can name your virtual environment whatever you'd like. An obvious and useful choice is 'proctor.'
I will assume that is the name you've chosen in the following examples.

 * `conda create -n proctor python=3.6 anaconda`
 
 This will create a virtual environment called 'proctor' on your local machine,
 and will install all necessary packages to support the specified Python environment.

#### Activate Virtual Environment
Because you can have multiple virtual environments on your machine, you need to choose
one in which to work. This is called your "active environment." The active environment
governs where subsequent Python packages and source code get installed. Packages installed 
into one virtual environment are isolated from those in all other virtual environments. 
Along these lines, it's important to have an active environment in which to work. 

If you are using miniconda:
* `conda env list` will display a list of existing environments
* `source activate proctor` will make proctor your working environment

Now that you have activated your virtual environment, you're ready to download
the Proctor source code.

### Get Source Code from GitLab
You can obtain Proctor's source code from WIT's GitLab server. Of course, you must have an
active account on the server to access its repositories.

* Clone Proctor's source repo to a local git-managed directory<br/>
https://eagle.cs.wit.edu/puopoloj1/proctor.git

   The repo contains a file called <i>requirements.txt</i>. The Python 3 package manager, 
pip3, uses this file to ensure all required packages are installed. 

* `pip3 install -r requirements.txt` to install required packages

### Using a Docker Image
A Docker image is a preconfigured environment that hosts a base operating system and 
various applications packages. Proctor is available as a Docker image that includes
the following:

* CentOS
* Java 8 JDK
* JUnit 4.12
* Python 3.8
* Proctor source code
* Starter configuration file

Download the Proctor Docker image.

## How Proctor Works
To understand the rest of the this document, it's important to take a few minutes to understand how
Proctor works and the assumptions it makes. First, let's take a look at the basic workflow:

![Proctor Workflow](http://wit.jpuopolo.us/wp-content/uploads/2019/04/workflow-e1555163566452.png)

Note that the document explains exactly _how_ to do the following things later. For now, it's important
to understand the overall concepts and structure of the application. 

### Logging In 
Proctor can manage groups on and download (clone) projects from the GitLab server via the GitLab API. 
To use the API, Proctor needs to log into the GitLab server with valid credentials. To do this, Proctor
uses the private token associated with your GitLab account. The private token is a secure replacement 
for a user ID and password. You can find your private token in your GitLab account under 
[Profile Settings](https://eagle.cs.wit.edu/profile/account). 
You will provide your private token in Proctor's configuration file, discussed in the next section.

### Local Working Directory
The working directory is the root directory on your local machine where Proctor keeps its log files and to
which it clones projects. For purposes of this document, let's suppose we have a directory called 
`~/procotor/wd` as the working directory.

### Cloning
Cloning is the process of copying a source code repository (repo) from the GitLab server to your local machine.
When Proctor clones a project, e.g., `PA1`, it creates a directory under the working directory with the
name of the project. So, given the above definitions, if we use Proctor to clone `PA1`, Proctor
will create a directory called `~/proctor/wd/PA1`. 

When Proctor subsequently clones student projects for `PA1`,
it will create a subdirectory per student. For example, if you clone `PA1` for student jonesx@wit.edu,
Proctor will create a directory called `~/proctor/wd/PA1/jonesx@wit.edu` and will copy the source repo
here.

### Grading
Before you can grade a project, you must have previously cloned it. The grading function expects the
project's source code and unit tests to be available on the local machine. The following is an example
of the `pa1-review-student-master` project used in COMP1050.


![PA1 Source Tree](http://wit.jpuopolo.us/wp-content/uploads/2019/04/src-tree-example.png)

<br/>This example demonstrates the following:

* We are in a subdirectory of Proctor's working directory, named consistently with the project.
* We've cloned 2 projects from the server, one for barretj@wit.edu and one for puopoloj1@wit.edu.
* The `src` directory serves as the root of the project's source code. This is a common convention.
* The project's source code is defined to be in the package `edu.wit.cs.comp1050`.
* The project's unit tests are in the `tests` subdirectory.
* The project's test suite (the class that runs all the other tests) is called `TestSuite`. 

It's important to understand these directories and paths in order to configure Proctor properly
via its configuration file, discussed shortly.

Grading a project consists of Proctor
* checking to see if the project is on time
* building the project's source code (using `javac`) 
* building the associated unit tests (generally packaged as part of the project)
* running the unit tests (using `java` and `JUnit`)

Proctor can, optionally, run a set of additional unit tests as specified by the instructor. 
To run your unit tests, make sure to provide `instructor_test_suite_dir` and `instructor_test_suite` 
keys under the given project section of the configuration file. If these keys are found, Proctor will 
attempt to load the specified test suite and run the tests against the project under consideration. 
Note: While Proctor builds the project's source code and the internal unit tests, it does _not_ 
attempt to build the instructor's test suite. The instructor will have had compiled the test suite beforehand.  

It's interesting to note that the instructor's tests do not need to be copied to the project/source code
under test. Using the values in the configuration file and "intelligent pathing", Proctor can,
in essence, "apply" the instructor's test to the project. Only a single copy of the instructor's tests need
exist. 

As part of the grading process, Proctor creates a gradebook file named `grades-N.csv`, runs all unit tests, 
and identifies the number of tests that pass out of the total. All of the information regarding each graded project 
per student is written to the gradebook file. The _N_ in the gradebook name is like a "version number". It is 
automatically incremented and appended to the gradebook's name to prevent accidental overwrites over multiple 
grading runs. The highest _N_ indicates the most recently run gradebook.
   

### Managing Groups
* ADD TO DIAGRAM and EXPLAIN HERE

Now that we have a high-level understanding of how Proctor works, we're ready to get into the details
of configuring it. 
 
 
## Configuring Proctor
Proctor uses <b>a single configuration file</b> to enable it do it's job. Both the GitLab repo
and the Docker image ship with a basic configuration file that you'll need to edit. 
This section describes the configuration file in detail.

### Name 
* Name the configuration file `.proctor.cfg`
* Put `.proctor.cfg` in your home directory, e.g., `~` on Linux and MacOS 

If Proctor does not find the configuration file in your home directory, it will attempt to use
the current working directory.

### Format
The configuration file uses a simple INI format, consisting of one or more sections, each
containing zero or more name-value pairs. For example:

> [GitLabServer] <br/>
> url = https://eagle.cs.wit.edu/

Here we have a section called _GitLabServer_ that contains a single name-value pair.

### Configuration File Details
The configuration file is critical. It contains all of the information Proctor needs
to function properly. The following table explains the valid sections, keys and their uses.

Section | Names | Values
------- | ----- | ------
**`[Proctor]`** | | **Application-level configuration**
| | `working_dir` | Name of Proctor's working directory, to which it clones git repos and writes log files.
| | `console_log_level` | Log level threshold. Messages at this level or greater appear in the console output. Uses the [Python logging levels](https://docs.python.org/3/library/logging.html). Set this value to `DEBUG` to see all log messages, `INFO` see to general messages and hide low-level details (recommended), and higher values to see only warnings, errors, and critical errors.  
| | `logfile_name` | Name of file that captures all logging output, created in Proctor's `working_dir`. Captures all logging information. To suppress file logging, remove the key or provide no value.
**`[GitLabServer]`** | | **GitLab Server endpoint and login information** 
| | `url` | URL to the GitLab server that houses projects. You must have a valid account on this server, of course.
| | `group_path_prefix` | Every group on the GitLab server is associated with a directory structure. The prefix is a unique moniker under which group elements are created, preventing conflicts (much like we use com.xyz to name Java packages). Suggest using your WIT username.
**`[GitLabUser]`** | | **User login information**
| | `private_token` | Private token associated with your GitLab user account. Replaces user ID and password. To find your private token, log into GitLab and look under [Profile Settings](https://eagle.cs.wit.edu/profile/account).
**`[Projects]`** | | **Information about default paths to source code, package names, and test suites.**
| | `default_src_dir` | Name of the subdirectory that contains the source code for students' projects. Most projects use `src` and store all source code, including unit tests, under this directory. 
| | `default_src_package` | Name of the package used by projects, e.g., `edu.wit.cs.comp1050`, relative to the `default_src_dir`. 
| | `default_student_test_suite` | Fully qualified name of the Java test suite class, relative to the `default_src_dir`.
| | `default_instructor_test_suite_dir` | Path to the directory where instructor's unit tests are stored.
| | `default_instuctor_test_suite` | Fully qualified name of the instructor's Java test suite class, relative to `default_instructor_test_suite_dir`.
| | `java_classpath` | Java classpath value to use when building and running Java programs. If absent, Proctor determines the correct value from the `CLASSPATH` environment variable, if set,  or from various working directories if not.
| | `junit_classpath` | Path including the 2 JAR files required to run JUnit 4.x tests. 
**`[SMTP]`** | | **SMTP login and port information**
| | `smtp_host` | URL or IP address to the SMTP server used to send emails
| | `smtp_port` | Port to use to communicate with the SMTP server
| | `smtp_user` | Your WIT email address
| | `smtp_password` | Your WIT email password 
**`<[project-name]>`** | | **One section per project, e.g., `[pa1-review-student-master]`.**
| | `due_dt` | Project's due datetime (date and time) in UTC format. Proctor compares this value to the project's last commit date on the server to determine if the project is on-time or late.
| | `src_dir`, `student_test_suite`, etc. | Project-specific overrides of the `default_` keys from the `[Projects]` section. In other words, if you want `[project-name]` to use a specific source package that overrides the default, you'd add a `src_package` key under `[project-name]`. Note the absence of the `default_` in the key name.

#### Example
The following is an example of a configured `.proctor.cfg` file:

```
[Proctor] 
working_dir = /Users/johnpuopolo/Adventure/proctor_wd
console_log_level = INFO
logfile_name = proctor.log

[GitLabServer]
url = https://eagle.cs.wit.edu/
group_path_prefix = puopoloj1

[GitLabUser]
private_token = ********************

[Projects]
default_src_dir = src
default_src_package = edu.wit.cs.comp1050
default_student_test_suite = edu.wit.cs.comp1050.tests.TestSuite
default_instructor_test_suite_dir = {Proctor.working_dir}/grading
default_instructor_test_suite = edu.wit.cs.comp1050.grading.PA3aGrading

java_classpath = ''
junit_path = {Proctor.working_dir}/JUnitRunner/lib/junit-4.12.jar:{Proctor.working_dir}/JUnitRunner/lib/hamcrest-core-1.3.jar

[SMTP]
smtp_host = smtp.office365.com
smtp_port = 587
smtp_user = puopoloj1@wit.edu
smtp_pwd = *****

[pa1-review-student-master]
due_dt = 2019-03-05T16:00:00-0500
src_package = com.xyz

[pa3-oopcli-student-master]
due_dt = 2018-03-24T00:00:00-0500
```

Note that the configuration file supports intelligent replacement values. In the sample
configuration file above, we see that the `junit_path` contains `{Proctor.working_dir}`.
This tells the configuration manager to replace `{Proctor.working_dir}` with the value of
the `working_dir` key found in the `Proctor` section. 

###Project Overrides
The configuration file contains one section per project. In the example above, we see `[pa1-review-student-master]` 
and `[pa3-oopcli-student-master]`. In addition to the `due_dt` key, these project
sections can contain project-specific keys that override the associated `[Projects]` defaults.

Here's how it works. When Proctor needs to determine a value for a given project, e.g., 
the source package (`src_package`), it checks the project's section, e.g., `[pa1-review-student-master]`
for the key. In this example, it would check `[pa1-review-student-master]` for the 
`src_package` key. If it finds it, it uses it. If not, Proctor will prepend the key name with `default_` and
check to see if that key (`default_src_package`) appears in the `[Projects]` section. 

So, Proctor always checks the individual project section first. If it can't find the key there, it 
will add `default_` to the key name and check the `[Projects]` section. In this way, individual
projects can override the general defaults on a per-key basis. You many never need to override the defaults, 
but hey, never say never.
  
## Running Proctor
Now that you have Proctor configured, it's time to run this bad boy.

### Command & Paramters
This sections describes each command, its parameters, and what happens when you execute it. Note that many
of the command use information from the configuration file. 

Command | Parameter | Required? | Description
--- | --- | --- | ---
**`glping`** | | | **Verifies communication with and access to the GitLab server**
**`clone`** | | | **Clones a given project for one or more students**
| | --project | Yes | Name of the assignment, lab or project to clone, e.g., `pa1-review-student-master`
| | --emails | Yes | Name of a file containing student/project owner emails. Proctor clones the given project for each email listed in the file. The format is expected to be one email per line.
| | --force | No | If present, forces overwrite of existing target directories on the local machine. If target directories exist, cloning will fail unless specified.
**`grade`** | | | **Grades a given project for one or more students**
| | --project | Yes | Name of the assignment, lab or project to grade, e.g., `pa1-review-student-master`
| | --emails | Yes | Name of a file containing student/project owner emails. Proctor grades the given project for each email listed in the file. The format is expected to be one email per line.
| | --chide | No | If present, sends reminder emails to students whose project was not found for grading.
**`group create`** | | | **Creates GitLab groups**
| | --groupname | Yes | Name of the group to create
**`group append`** | | | **Adds users/emails to a GitLab group**
| | --groupname | Yes | Name of the group to which to add users
| | --emails | Yes | Name of a file containing users/emails. The users in the file are added to the specified group.

#### Command Examples
The following examples demonstrate all of Proctor's valid commands and their associated parameters.
The most sophisticated command is `grade` as it accesses the GitLab server, builds the project's source code,
builds the unit tests associated with the project, runs the associated unit tests, and optionally runs the
unit tests specified by the instructor in the configuration file. The result of each step is stored in the 
created gradebook file.
```
$ glping
$ clone --project=pa1-review-student-master --emails=proctor_wd/comp1050.txt
$ clone --project=oop3-cli --emails=mystudents.txt --force
$ grade --project=pa1-review-student-master --emails=mydir/mystudents.txt 
$ grade --project=someproject --emails=allstudents.txt --chide
$ group create --groupname=extracredit
$ group append --groupname=extracredit --emails=students.txt
 ```
## Wrap Up
Proctor is cool.





