# workload

<tt>workload</tt> is a simplistic script for measuring the time spent on specified tasks via command line calls. 
The following steps are needed to use this tool:

## Prerequisities
- running installation of <tt>conda</tt>
- python version >= 3.5

## Installation
1. clone this repository, go to repository
2. create conda environment from yml file: <tt>conda env create --file .workload.yml</tt>
3. update the [config.yaml](config.yaml) file accordingly:
  - acronyms: the names you want to give your tasks
  - goal: the number of hours you want to spent occupied with the tasks each day
  - folder: path to this repository
    - this repository will be used as a safing location for needed files while this tool works
    - the files will be either saved directly in the main folder or in tasks/
3. add the folowing function to your bashrc

You can basically name it any way you want, the obvious name is recommended.

    function workload {
      /path/to/repository/workload/workload.py $1 $2 $3
    }

4. Optional: If you want to see the goal and the remaining hours each time you refresh you Bash, add the following command at a fitting location in your bashrc:

It will look like this in your terminal:

    Your goal are	 7:0 hours.
    Already done:	 3:20 hours.
    Still to do:	 3:40 hours.
  
Command:
  
    workload overview goal
    
## Usage
Once you have set up the config file and reloaded the Bash after adding the function, you can use the tool accordingly:
1. Starting a task

        workload start TASK
  
2. Stopping a task

        workload end
  
3. Showing the overviews:

        workload overview [day|week|month|year|goal]
  Only the task you spent some time on are shown in the overviews.
 
### Help
#### General
    workload --help

        usage: workload [-h] [--version] {start,end,overview} ...

        Simplistic Measurement for Working Time

        positional arguments:
        {start,end,overview}
        start               Starting a Time Measurement
        end                 Ending a Time Measurement
        overview            Getting an Overview over Spent Time

        optional arguments:
        -h, --help            show this help message and exit
        --version, -v         show program's version number and exit
    
#### Start
    workload start --help 
        usage: workload start [-h] task1, task2, task3, task4}

        positional arguments:
        {ma,it,cb,others}

        optional arguments:
        -h, --help         show this help message and exit

#### End
    workload end --help 
    
        usage: workload end [-h]

        positional arguments:
        end

        optional arguments:
        -h, --help  show this help message and exit
  
#### Overview
    workload overview --help
    
        usage: workload overview [-h] {day,week,month,year,goal}

        positional arguments:
        {day,week,month,year,goal}


