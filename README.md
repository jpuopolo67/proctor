# Proctor!

## User Guide
_Last update: 2019-May-09_

## Welcome
_Proctor_ is a Python 3.6 command-line application that enables you to grade Java-based projects. 
It is intended for use by Wentworth Institute of Technology (WIT) instructors. This document serves 
as a user guide and reference.

The application runs on various operating systems including Windows, Linux and MacOS, and relies 
on having network access to a GitLab server. 

It has been tested on the following operating systems:
* MacOS Mojave 10.15
* Alpine Linux v3.9

Note that Proctor is inspired heavily by Derbinsy's _witgrade_, offering increased simplicity at the 
cost of fewer features.

## What Can I Do with Proctor?
Proctor enables you to perform the following actions:
* Display application configuration information
* Verify access to a GitLab server
* List projects owned by a given user
* Clone projects from a GitLab server to your local machine
* Grade projects that you've cloned
* Manage groups on a GitLab server
* Refresh (re-clone & re-grade) projects for a given set of students

### How Proctor Works
Before we move on, it's important to take a few minutes to understand how
Proctor works. First, let's take a look at the basic workflow:

![Proctor Workflow](http://wit.jpuopolo.us/wp-content/uploads/2019/04/workflow-1.png)

In order for Proctor to work correctly, it needs access to a GitLab server so that it can 
clone projects and fetch metadata such as a project's last commit date.
Make sure you have network access to the GitLab server and that you have a valid, active account. 

The basic workflow is as follows:
1. Verify your connection to the GitLab server: `proctor glping`
2. Clone a project for a set of students: `proctor clone --project=pa --emails=students.txt` 
3. Grade a project for a set of students: `proctor grade --project=pa --emails=students.txt`
4. Manage server groups: `proctor group create --groupname=cs2-fall19`
   <br/>Add students to a group: `proctor group append --groupname=cs2-fall19 --emails=students.txt`

We discuss each of these in greater detail throughout this document.

When dealing with groups of students and multiple class sections on
the GitLab server, it's useful to be able to grant permissions on a group basis.
Proctor supplies a few convenience commands to create groups, but does attempt to replicate 
all of GitLab's group-management features. 

## Setting Up Your Enviroment
Before you can run Proctor, you need a working environment. Specifically, you need 
the following SDKs and associated run-times installed on your computer:

* Java 8 or higher. All references to Java hereafter assume 8 or higher.
* JUnit 4.x. The application was tested with JUnit 4.12. 
* Python 3.6 or higher. All references to Python hereafter assume 3.6 or higher.
* Git (most recent)
* _Optional:_ Docker (most recent)

### No Eclipse Necessary
Proctor does not rely on any particular Java IDE or tooling. So long as the required SDKs, e.g., Java 8,
Python 3, etc. are installed and set up normally on your local machine, you do not need Eclipse or any additional
tooling.

### Local Install or Docker Image
You have two choices of how to set up the Proctor environment:

* You can set up the required tech stack yourself on a local machine or in the cloud
* You can download and use a preconfigured Docker image (recommended)

The following directions explain how to set up a local environment. If you'd
rather use the Docker image, you can skip directly to the section 
[_Using a Docker Image_](#using-a-docker-image)

### Download, Install and Configure Java & JUnit
Because Proctor is designed to help grade Java and JUnit-based projects, you need to have
the Java SDK installed, as well as a copy of JUnit. Proctor will use these tools  to build and test projects.

* [Java JDK Download](https://www.oracle.com/technetwork/java/javase/downloads/index.html)
* [JUnit 4.x Download](https://junit.org/junit4/)

Download and install the Java JDK and JUnit framework, and configure them normally. There is 
nothing special you need to do with these to make Proctor work properly.

### Set Up Git
Download and install the most recent version of Git.
* [Download Git](https://git-scm.com/downloads)

### Set Up Python & Python Virtual Environment
Python virtual environments are isolated sandboxes for Python distributions and projects.
Each virtual environment is a complelety separate installation of Python, enabling you to have 
multiple copies and versions of Python running on your machine at the same time. 
Each project can maintain its own set of modules, dependencies, etc.

There are several tools that enable you to manage virtual environments including _virtualenv_ and
_miniconda_. I prefer miniconda, and subsequent directions are miniconda-relative. That said, 
you should use the tool with which you're most comfortable or familiar. You can read about each 
and download your favorite:

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
You can name your virtual environment whatever you'd like. An obvious and useful choice is _proctor_.
I will assume that is the name you've chosen in the following example:

 * `conda create -n proctor python=3.6 anaconda`
 
 This will create a virtual environment called _proctor_ on your local machine,
 and will install all necessary packages to support the specified Python environment.

#### Activate Virtual Environment
Because you can have multiple virtual environments on your machine, you need to choose
one in which to work. This is called your _active environment_. The active environment
governs where subsequent Python packages and source code get installed. Packages installed 
into one virtual environment are isolated from those in all other virtual environments. 

If you are using miniconda, run the following commands:
* `conda env list` will display a list of existing environments
* `source activate proctor` will make _proctor_ your working environment

Now that you have activated your virtual environment, you're ready to download
the Proctor source code.

### Get Source Code from GitLab
You can obtain Proctor's source code from WIT's GitLab server. Of course, you must have an
active account on the server to access its repositories.

* Clone Proctor's source repo to a local git-managed directory<br/>
https://eagle.cs.wit.edu/puopoloj1/proctor.git

The repo contains a file called `requirements.txt`. The Python 3 package manager, 
`pip3`, uses this file to download and install all packages that Proctor needs to work properly. 
Run the following command:

* `pip3 install -r requirements.txt`

And that's it! You are now ready to edit Proctor's configuration file.

### Using a Docker Image
A Docker image is a preconfigured environment that hosts a base operating system and 
various applications packages. Proctor is available as a Docker image that includes
the following:

* Alpine Linux
* Java 8 JDK
* JUnit 4.12
* Python 3.6
* Git
* Proctor source code
* Starter configuration file
* VIM editor

This Docker image was created for Linux-based systems and is not compatible with Windows.
To use this image:

* Make sure you have [Docker](https://www.docker.com/) installed and running on your local machine
* Download the image from the Docker Hub registry:<br/>
`docker pull jpuopolo/proctor:latest`

Before running a container based on this image, select a _local directory on your host_ where you can 
keep data that will persist between container runs. After editing the starter `.proctor.cfg` file, you 
will want to keep a separate copy in case the container stops or dies, e.g., if your machine reboots. 
For our purposes, we'll assume this directory is `/home/me/pdata`.

* Run a container based on the image using the _-v_ option<br/><br/>
`docker run -it -v /home/me/pdata:/data proctor`<br/>

    * The docker image makes the `proctor.py` file executable, so you can enter<br/>
`proctor.py cmd --parameters`

    * The container that Docker creates is preconfigured with all of the software you need, 
a starter `.proctor.cfg` file, and the following directories:

    * `/root` 
        * You will find the starter `.proctor.cfg` in this directory. You need to edit this file and 
        supply some values, discussed shortly.
    * `/home/proctor`
        * Location of Proctor's source code. You run the application from this directory.
    * `/home/proctor/work`
        * Proctor's default working directory, where cloned projects and log files live.
    * `/data`
        * Container directory that's mapped to a host directory. It's 
        used to retain data between container runs, e.g., your edited `.proctor.cfg` file. 
        Each time you run a new container based on the Proctor image, you will lose all edits, including
        those to your configuration file. So, keep a copy of `.proctor.cfg` in `/data` and copy it to `/root`
        whenever you start a new container. Note that you can also use 
        `/data` to copy instructor test files, JUnit suites, etc. from the host machine to the container. 

* Edit the configuration file<br/>
`vim /root/.proctor.cfg`<br/>
    * The image ships with _vim_, a popular text editor.

* Supply values for the following keys. Note that you can find information about these keys
and what they do in the section [_Configuration File Details_](#configuration-file-details)
    * `group_path_prefix`
    * `private_token`
    * `smtp_user`
    * `smtp_pwd`

* You can optionally fill in or change the values for the `default_` keys in
the `[Defaults]` section of the configuration file.

* Add `[<assignment section>]` for each assignment you want to grade
    * You can (and probably should) treat the configuration file as a living document. You can 
    update it with assignment information, due dates, etc. in the future. You don't need to do 
    all of this on initial setup.
    
After you've made your initial updates to the configuration file, make a copy to the `/data` directory:<br/>
`cp /root/.proctor.cfg /data`<br/>

You will now have a copy of `.proctor.cfg` in your host's `/home/me/pdata` directory. 
Having a copy will prove useful should your container meet an untimely death (_maniacal laughter here_).<br/>

**Note: Repeat this copy step any time you make a change to `/root/.proctor.cfg`.**


# Configuring Proctor
Proctor uses a **single configuration file** to enable it do it's job. Both the GitLab repo
and the Docker image ship with a basic configuration file that you'll need to edit. 
This section describes the configuration file in detail.

### Name 
* Name the configuration file `.proctor.cfg`
* Put `.proctor.cfg` in your home directory, e.g., `~` on Linux and MacOS 

If Proctor does not find the configuration file in your home directory, it will attempt to use
the shell's current working directory.

### Format
The configuration file uses a simple [INI format](https://en.wikipedia.org/wiki/INI_file), 
consisting of one or more sections, each containing zero or more name-value pairs. For example:

> ; Generic format
> [Section] <br/>
> key1 = value1 <br/>
> key2 = value2
>
> ; Example
> [GitLabServer] <br/>
> url = https://eagle.cs.wit.edu/

### Configuration File Details
The configuration file is critical. It contains all of the information Proctor needs
to function properly. The following table explains the valid sections, the keys and 
their meaning, and how to use them.

Section & Key Name | Value Description
--- | ---
**`[Proctor]`** | **Application-level configuration** |
<i>working_dir</i> | Name of Proctor's working directory, to which it clones git repos and writes log files.
<i>console_log_level</i> | Log level threshold. Messages at this level or greater appear in the console output. Uses the [Python logging levels](https://docs.python.org/3/library/logging.html). Set this value to `DEBUG` to see all log messages, `INFO` see to general messages and hide low-level details (recommended), and higher values to see only warnings, errors, and critical errors.  
<i>logfile_name</i> | Name of file that captures all logging output, created in Proctor's `working_dir`. Supports _YYYYMMDD_ date replacement. Captures all logging information. To suppress file logging, remove the key or provide no value.
**`[GitLabServer]`** | **GitLab Server endpoint and login information** 
<i>url</i> | URL to the GitLab server that houses projects. You must have a valid account on this server, of course.
<i>group_path_prefix</i> | Every group on the GitLab server is associated with a directory structure. The prefix is a unique moniker under which group elements are created, preventing conflicts (much like we use com.xyz to name Java packages). Suggest using your WIT username.
**`[GitLabUser]`** | **User login information**
<i>private_token</i> | Private token associated with your GitLab user account. To find your private token, log into GitLab and look under [Profile Settings](https://eagle.cs.wit.edu/profile/account).
**`[Defaults]`** | **Information about default paths to source code, package names, and test suites.**
<i>default_src_dir</i> | Name of the subdirectory that contains the source code for students' projects. Most projects use _src_ and store all source code, including unit tests, under this directory. 
<i>default_src_package</i> | Name of the package used by projects, e.g., _edu.wit.cs.comp1050_, relative to the _default_src_dir_. 
<i>default_student_test_suite</i> | Fully qualified name of the Java test suite class, relative to the _default_src_dir_.
<i>default_instructor_test_suite_dir</i> | Path to the directory where instructor's unit tests are stored.
<i>default_instuctor_test_suite</i> | Fully qualified name of the instructor's Java test suite class, relative to _default_instructor_test_suite_dir_.
<i>java_classpath</i> | Java _classpath_ value to use when building and running Java programs. If absent, Proctor determines the value from the _CLASSPATH_ environment variable, if set,  or from various working directories if not.
<i>junit_classpath</i> | Path that includes the two JUnit JAR files required to run JUnit 4.x tests. 
**`[Projects]`** | **List of all projects used for various commands including _srefresh_.**
<i>default_src_dir</i> | Name of the subdirectory that contains the source code for students' projects. Most projects use _src_ and store all source code, including unit tests, under this directory. 
<i>default_src_package</i> | Name of the package used by projects, e.g., _edu.wit.cs.comp1050_, relative to the _default_src_dir_. 
<i>default_student_test_suite</i> | Fully qualified name of the Java test suite class, relative to the _default_src_dir_.
<i>default_instructor_test_suite_dir</i> | Path to the directory where instructor's unit tests are stored.
<i>default_instuctor_test_suite</i> | Fully qualified name of the instructor's Java test suite class, relative to _default_instructor_test_suite_dir_.
<i>java_classpath</i> | Java _classpath_ value to use when building and running Java programs. If absent, Proctor determines the value from the _CLASSPATH_ environment variable, if set,  or from various working directories if not.
<i>junit_classpath </i>| Path that includes the two JUnit JAR files required to run JUnit 4.x tests. 
**`[SMTP]`** | **SMTP login and port information**
<i>smtp_host</i> | URL or IP address to the SMTP server used to send emails
<i>smtp_port</i> | Port to use to communicate with the SMTP server
<i>smtp_user</i> | Your WIT email address
<i>smtp_password</i> | Your WIT email password 
**`<[project-name]>`** | **One section per project, e.g., `[pa1-review-student-master]`**
<i>due_dt</i> | Project's due date and time in UTC format. Proctor compares this value to the project's last commit date on the server to determine timeliness.
<i>src_dir</i><br/><i></i>student_test_suite</i><br/>...| Project-specific overrides of the `[Defaults]` _default__ keys. 

**We discuss these keys in more detail in the relevant sections below.**
 

#### Example
The following is an example of a configured `.proctor.cfg` file:

```
[Proctor]
working_dir = /Users/johnpuopolo/Adventure/proctor_wd
console_log_level = INFO
logfile_name = proctor-YYYYMMDD.log

[GitLabServer]
url = https://eagle.cs.wit.edu/
group_path_prefix = puopoloj1

[GitLabUser]
private_token = ***

[Projects]
pa1-review-student-master = Java review
pa2-review-student-master = PA2
pa3-oopcli-student-master = PA3
pa4-oop2-student-master = PA4
pa5-oop3-student-master = PA5

[Defaults]
default_src_dir = src
default_src_package = edu.wit.cs.comp1050
default_student_test_suite = edu.wit.cs.comp1050.tests.TestSuite
default_instructor_test_suite_dir =
default_instructor_test_suite =

; Java-specific values
java_classpath =
junit_path = {Proctor.working_dir}/JUnitRunner/lib/junit4.jar:{Proctor.working_dir}/JUnitRunner/lib/hamcrest-core-1.3.jar

[pa1-review-student-master]
due_dt = 2019-04-19T04:00:00-0400

[pa2-review-student-master]
due_dt = 2019-04-19T04:00:00-0400

[pa3-oopcli-student-master]
due_dt = 2019-04-19T04:00:00-0400

[pa4-oop2-student-master]
due_dt = 2019-04-19T04:00:00-0400

[pa5-oop3-student-master]
due_dt = 2019-04-19T04:00:00-0400
src_dir = example/src/dir/not/default
src_package = example.src.pkg.not.default

[SMTP]
smtp_host = smtp.office365.com
smtp_port = 587
smtp_user = puopoloj1@wit.edu
smtp_pwd = ***
```

Note that the configuration file supports intelligent replacement values. In the sample
above, we see that the `junit_path` contains `{Proctor.working_dir}`.
This tells the configuration manager to replace `{Proctor.working_dir}` with the value of
the `working_dir` key found in the `Proctor` section. 

### Project Overrides
At the end of the configuration file, can add one section per project. In the example above, we see `[pa1-review-student-master]` 
and `[pa3-oopcli-student-master]`. In addition to the `due_dt` key, these project
sections can contain project-specific keys that override the associated `[Projects]` defaults.

Here's how it works. When Proctor needs to determine a value for a given project, e.g., 
the source package (`src_package`), it checks the project's section, e.g., `[pa1-review-student-master]`
for the key. In this example, it would check `[pa1-review-student-master]` for the 
`src_package` key. If it finds it, it uses it. If not, Proctor will prepend the key name with `default_` and
check to see if that key (`default_src_package`) appears in the `[Projects]` section. 

So, Proctor always checks the individual project section first. If it can't find the key there, it 
will add `default_` to the beginning of the key name and then check the `[Projects]` section. In this way, individual
projects can override the general defaults on a per-key basis. You will most likely do this if
you supply your own (instructor) unit tests as part of the grading process, discussed shortly.

## Running Proctor

### Logging In 
Proctor communicates with the GitLab server via the GitLab API. The WIT GitLab server, at the time of this
writing, is configured to use the GitLab 3.x API. 
To use the API, Proctor needs valid credentials, represented by your _private token_. 
The private token is a secure replacement for a basic user ID and password. You can find your 
private token in your GitLab account under [Profile Settings](https://eagle.cs.wit.edu/profile/account). 
You will provide your private token in Proctor's configuration file, discussed in the next section.

### Using the Local Working Directory
The _working directory_ is a directory on local machine where Proctor keeps its log files and to
which it clones projects. For purposes of this document, we'll assume 
`~/procotor/wd` as the working directory.

### Logging
Logging in an important part of any application. Proctor uses the Python logging framework and offers
two related but independent logging streams: the console and a logging file.
 
#### The Console
You can set the logging level for the console using the `console_log_level` key in the 
configuration file. Valid values include:

Level | When It's Used
--- | ---
`DEBUG` | Detailed information, typically of interest only when diagnosing problems.
`INFO` | Confirmation that things are working as expected.
`WARNING` | An indication that something unexpected happened, or indicative of some problem in the near future e.g. ‘disk space low’. The software is still working as expected.
`ERROR` | Due to a more serious problem, the software has not been able to perform some function.
`CRITICAL` | A serious error, indicating that the program itself may be unable to continue running.

#### A Logging File
To capture logging output to a file, you must provide a value for the `logfile_name` key in 
the configuration file. The log file will appear in Proctor's working directory (see the `working_dir` 
configuration key). If the file does not exists, it will be created. If it does 
exist, it will be opened in append mode. The log file captures _all_ logging output, independent of the console.

Note that the log file processor recognizes one special pattern: _YYYYMMDD_. If you include this string
anywhere in the `logfile_name` value, Proctor will replace it with the actual date. This enables you to
create log files per day.

### Displaying Configuration Information
To see basic configuration information, execute the `config` command. To display basic information
plus the contents of the configuration file, add the `--verbose` switch.

### Verifying Access to GitLab Server
In order to verify that you can access and log into the GitLab server specified in the configuration
file, you can use the GitLab ping command, `glping`. This command will verify connectivity to the server
and will display project summary information.

### Listing Projects by Owner Email
Sometimes it's useful to list all of the projects that a given student has uploaded to the server and made available
to you. To do this, execute the `projects --owner=<owner email>` command. This will list all of the projects
uploaded to the server by the specificed user to which you have access.

This command includes two more options:
* `--emails`. Name of a file that contains one or more email addresses for which to list projects.
* `--share`. If present, will send a copy of the owner's project list to the owner.

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

It's important to understand these directories and paths so that you can  
configure the application properly. We discuss this in a moment.

Grading a project consists of Proctor performing the following actions on
a previously cloned project:

* checking to see if the project is on time
* building the project's source code (using `javac`) 
* building the associated unit tests (generally packaged as part of the project)
* running the unit tests (using `java` and `JUnit`)

Proctor can, optionally, run a set of additional unit tests as specified by the instructor. 
To run your (instructor's) unit tests, make sure to provide the 
`instructor_test_suite_dir` and `instructor_test_suite` keys under the given _[project]_ section of the 
configuration file. If these keys are found, Proctor will 
attempt to load the specified test suite and run the tests against the project. 

**Note:** While Proctor builds the project's source code and the internal unit tests, it does _not_ 
attempt to build the instructor's test suite. The instructor will have had compiled the test suite beforehand. 

In general, the instructor can build his/her unit test suite against any one of the projects
under consideration. For example, let's suppose we are grading _TheProject_ and have cloned it
for 2 students: s1@wit.edu and s2@wit.edu. We can build our test suite, e.g., _GradingSuite_, against
_either_ student's _TheProject_ - it makes no difference. The compilation step simply needs compile-time 
references to the classes that will be tested.

To emphasize the point, the instructor's tests do not need to be copied to the project/source code
folder under test. Using the values in the configuration file and "intelligent paths", Proctor 
in essence, applies the instructor's tests to the project across all students.
Only a single, compiled copy of the instructor's tests need exist. 

As part of the grading process, Proctor creates a grade file named `grades-N.csv`. As it perform each
grading step, e.g., building source and running unit tests, it writes the results to the grade book.  
The _N_ in the grade book name is like a "version number". It is 
automatically incremented and appended to the grade book's name to prevent accidental overwrites over multiple 
grading runs. The highest _N_ indicates the most recent grades.

#### Grade Book Format
The grade book is a simple CSV file that contains the following columns:

Column Name | Type | Description | Example
--- | --- | --- | ---
**`project_name`** | string | Name of project graded | pa1-review-student-master
**`email`** | string | Email of student for which the project is graded | puopoloj1@wit.edu
**`due_dt`** | datetime | Project due date and time in UTC format | 2019-03-05T16:00:00-0500
**`latest_commit_dt`** | datetime | Date and time of most recent Git commit from server | 2019-03-04T13:27:09-0500
**`is_ontime`** | boolean | True if the project latest commit <= due date | TRUE
**`days`** | integer | Number of days difference between latest commit and due date. If project on time, this is the number of days early, otherwise it's the number of days late. | 4
**`hours`** | integer | Number of hours (minus days) difference between latest commit and due date. If project on time, this is the number of hours early, otherwise it's the number of hours late. | 11
**`mins`** | integer | Number of minutes (minus days and hours) difference between latest commit and due date. If project on time, this is the number of minutes early, otherwise it's the number of minutes late. | 22
**`source_builds`** | boolean | True if project source code built successfully | FALSE
**`student_tests_build`** | boolean | True if all student's tests built successfully | TRUE
**`student_tests_ratio`** | float | Ratio of tests-passed/tests-executed | 0.89
**`instructor_tests_ratio`** | float | Ratio of instructor's tests-passed/tests-executed | 1.0
**`grade`** | string | Currently left blank. Instructor to manually fill or load in Excel and write formula to grade. | TBD
**`notes`** | string | Used by Proctor to add errors or issues encountered during grading | Proctor run notes

The grade book includes one row per student. So, if there are 25 students in your class and 
you are grading _TheProject_, you will have 25 rows in _TheProject_'s grade book. This assumes,
of course, that
you've included all 25 emails in the file that you used to execute the grading run.

### Refreshing
Sometimes it's useful to "refresh" projects. This means re-cloning and optionally re-grading one or 
more projects for one or more students. The command to do this in Proctor is `srefresh` (student refresh). 
The projects to refresh are listed in the `[Projects]` section of the configuration file. See the table
below in _Commands & Parameters_ for the options.
 
### Commands & Parameters
This sections describes each command, its parameters, and what happens when you execute it. Note that many
of the command use information from the configuration file. 

Command  | Parameter | Required? | Description
--- | --- | --- | ---
**`config`** | --verbose | No | Displays basic configuration information and the contents of the configuration file.
**`glping`** | _none_ | -- | Verifies access to the GitLab server.
**`projects`** | --owner | No | User email for which to find projects.
&nbsp; | --emails | No | Name of a file containing student (project owner) emails. Proctor fetches available project information for each email listed in the file. The format is expected to be one email per line.
&nbsp; | --share | No | If this flag is present, shares an owner's project list with that owner.
**`clone`** | --project | Yes | Name of the assignment, lab or project to clone.
&nbsp; | --emails | Yes | Name of a file containing student (project owner) emails. Proctor clones the given project for each email listed in the file. The format is expected to be one email per line.
&nbsp; | --force | No | If present, forces overwrite of existing target directories on the local machine. If target directories exist, cloning will fail unless specified.
**`grade`** | --project | Yes | Name of the assignment, lab or project to grade.
&nbsp; | --emails | Yes | Name of a file containing student/project owner emails. Proctor grades the given project for each email listed in the file. The format is expected to be one email per line.
&nbsp; | --chide | No | If present, sends reminder emails to students whose project was not found for grading.
**`group create`** | --groupname | Yes | Name of the group to create.
**`group append`** | --groupname | Yes | Name of the group to which to add users.
&nbsp; | --emails | Yes | Name of a file containing users/emails. The users in the file are added to the specified group.
**`srefresh`** | --owner | No | User email for which to refresh projects. The projects refreshed are those found in the `[Projects]` section of the configuration file.
&nbsp; | --emails | No | Name of a file containing student (project owner) emails. Proctor refreshes available projects for each email listed in the file. The format is expected to be one email per line.
&nbsp; | --grade | No | If present, instructs Proctor to re-grade the assigrments for the given student(s) after re-cloning completes.

#### Command Examples
The following examples demonstrate all of Proctor's valid commands and their associated parameters.
Assume each command begins with `python3 proctor.py `
```
$ python3 proctor.py...

    $ config
    $ config --verbose
    $ glping
    $ projects --owner=studentx@wit.edu
    $ projects --emails=all-students-comp1050.txt --share
    $ clone --project=pa1-review-student-master --emails=proctor_wd/comp1050.txt
    $ clone --project=oop3-cli --emails=mystudents.txt --force
    $ grade --project=pa1-review-student-master --emails=mydir/mystudents.txt 
    $ grade --project=someproject --emails=allstudents.txt --chide
    $ group create --groupname=extracredit
    $ group append --groupname=extracredit --emails=students.txt
    $ srefresh --owner=puopoloj1@wit.edu
    $ srefresh --emails=allstudents.txt
    $ srefresh --emails=allstudents.txt --grade  
 ```
 
## Future Enhancements
No single application can cover everyone's needs. I encourage folks to clone this project and contribute to it!
In fact, if you're teaching a Python class, perhaps assign additions, upgrades and bug fixes to the codebase.
Some ideas for enhancements include:

* Building the instructor/external unit tests 
* Enabling a separate step to build the source code independently of grading it
    * I couldn't think of a compelling use case for this, so left it out in this version
* Enhancing the group management functionality to remove people from groups, grant certain levels
of access to groups, etc.
* Replacing the simple CSV-style grade book with an Excel spreadsheet and adding grading formulas automatically
* Adding an upload feature to Blackboard and LConnect or, better yet, API-based integration
* Create a Windows-compatible Docker image and share it on Docker Hub

## Wrap Up
I hope that you find Proctor a useful and time-saving application. If you have any questions, or need more
information, I'd love to hear from you. Just drop me a note at my WIT email address: 
[puopoloj1@wit.edu](mailto:puopoloj1@wit.edu).








