# Specifications


## Contents
- [Introduction](#introduction)
- [Requirements](#requirements)
    - [Background](#background)
    - [Existing Tools](#existing-tools)
    - [Functional Requirements](#functional-requirements)
- [Implementation](#implementation)
    - [Selected Solution](#selected-solution)
    - [Feature Outline](#feature-outline)
    - [Development](#development)
    - [Deployment](#deployment)


# Introduction
This document describes the requirements and general design of the ODK Aggregation Tool GUI. Further details are found in other documents, for example user guides or developer documentation.


# Requirements


## Background
The Android app "ODK Collect" facilitates flexible mobile data collection by allowing forms to be defined XML, using the XForms standard. Data entered into these forms is recorded in XML files referred to as "instances". 

An instance XML file is created for each form response, analogous to how a paper form is photocopied for each participant to record their answers on. Unlike a paper form, the instance XML only records form name and version, and for each variable, the variable name and the value recorded.

In order to process and interpret the collected information, the instance XML data for each form must be collated into a single file, along with the following metadata for each form variable:

- What was the question text for the variable
- What is the data type of the variable
- For variables using choice lists, what is the label text for each choice value


## Existing Tools
The ODK Suite includes the following tools for managing instance XML data:

- ODK Aggregate: a web app
    - receives instance XML submitted over the Internet
    - collates received data by form definition
    - pairs instance data with metadata from most recent version of the form
    - multiple options for output, including: CSV, Google Sheets, JSON
- ODK Briefcase: a desktop app
    - "pulls" data from a device connected via USB, or local storage
    - collates received data by form definition
    - "pushes" data either to a local CSV file, or a server like ODK Aggregate


## Functional Requirements
An application which meets the following requirements is needed:

- Collate instance XML files located in local or mapped network storage
- Read form definitions from files located in local or mapped network storage
- Instance and form definitions files must be discovered by recursively searching the specified locations
- Produce a file for each form definition, across all versions of that form:
    - where metadata appears in more than one version, preference the most recent
    - if a variable appears in none of the discovered form definitions but appears in the instance data anyway, include it in the output as a text field named using the variable name
- The produced file must be readable / importable by Stata 12 or higher
- Form components or variables that do not store data directly must be excluded, for example read-only note fields, or group elements
- The produced file must include, or be accompanied by a DO file or similar that can attach, the following metadata:
    - Variable label, defined by the question text
    - Variable data type
    - Value labels for any variables using choice lists
- Minimal or no installation requirements
- Compatibility with Windows 7
- A non-commandline interface for users to interact with


[Back to Contents](#contents)


# Implementation


## Selected Solution
The app will be implemented as a new project, written in Python.

The ODK Briefcase app comes quite close to meeting the above requirements. The components relating to preparing files and metadata for Stata are not met, only the most recent form version metadata is included, and instance or form definition files are expected to be in the top level of one folder.

Ideally, ODK Briefcase would be adapted or extended for these functional requirements. Unfortunately, like many ODK Suite tools, development activity is hamstrung by an absence of unit tests and user acceptance scenarios / criteria, which are critical to ensuring that the app behaves as expected. Implementing these presents a significant barrier to be overcome before any new features can be introduced.

The existing ODK Tools GUI, which assists in processes related for deploying forms defined as XLSForms, has some components that can be recycled for this app. For example:

- Processes for preparing and packaging an executable GUI
- Reading metadata from an XLSForm
- Processing large amounts of files, including XML


## Feature Outline
The app should accept the following input:

- Paths to folders where:
    - the relevant forms definition XLSForms files are kept
    - the instance XML files are kept
    - the output files should be saved
- Intention to start, e.g. click a "Run" button

The app should do the following:

- Indicate to the user:
    - that the task has started
    - the outcome of the task, including errors encountered
    - if applicable and possible, suggestions on resolving errors
- Save the output files to the location specified by the user


## Development
The repository must include instructions for developers on how to set up the development environment, how to build the deployment package, a general introduction to the structure of the code, and inline or docstring comments explaining implementation details. A test suite must be prepared which validates the behaviour of the code, with as much coverage of usage scenarios as possible.

User acceptance testing will be conducted for each release candidate version by:

- Preparing a list of the known and expected usage scenarios, and success criteria
- Preparing a set of test files to work with
- Have users (ideally not involved in development) complete these scenarios
- The outcome (pass/fail) and any comments / requests should be recorded for each scenario

If any scenarios fail to meet success criteria, or feedback includes change requests not substantially changing the specifications, the changes will be incorporated in a new release candidate version. Subsequent test rounds should focus on changed components / the failed scenarios, but may repeat the full suite of scenarios if appropriate.


## Deployment
The app must be deployed as an executable that can be run by users, either from a local copy or from the mapped network storage. The folder(s) containing the app must include a user guide document, and any other relevant documentation for users.

Any relevant notes about a specific deployment must be included along with the deployment package.


[Back to Contents](#contents)


