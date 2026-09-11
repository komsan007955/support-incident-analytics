# Support Incident Analytics
## Prerequisites
- git
- python
## Installation and Setup
1. Clone the repository: `git clone https://github.com/komsan007955/support-incident-analytics.git`
2. Enter the scripts/powershell path: `cd support-incident-analytics\scripts\powershell`
3. Allow execution permission to all scripts in this path: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
4. Execute the setup script: `.\Setup.ps1`
## Configuration
1. Open config.conf on your text editor.
2. Change the input_filepath to the folder that stores the Excel files to be processed.
3. Change the output_filepath to the folder that stores the destination data.
## Validation
1. Make sure every Excel file name to be processed follows this format: Jira_[ddMMyy]_[hhmm]
## Run the Script
1. Make sure you're at the project home path.
2. Run the executing script: `.\scripts\powershell\Execute.ps1`