ROADMAP
=======

Feedback
--------

*It didn't work because libmagick was not installed.*

- Remove libmagic dependence from dtoolcore this also has the benefit of
  making dtoolcore cross platform
- Investigate pure Python implementations of libmagic
- Implement helper function for creating mimetype overlays
- Make use of mimetype overlay in dtool

*I want to be able to create more nested directory structures.*

- Expose the ability to create collections to dtool

*I want to be able to mark up an existing directory as a project.*

- Add ability to mark up a directory as a project to dtool
- Add ability to mark up a directory as a collection to dtool

*I want to keep my code and data together in a dataset.*

- Write up reasoning why this is a bad idea including:

  - It makes it easier to know what can be deleted
  - Things need to be treated differently, i.e. a datasets
    may need archiving, code may need to get into GitHub,
    manuscripts may need to go into Dropbox
  - Over time many-to-many relationships tend to develop
    between data and analyses, usually these are not apparent
    during the initial stages of the project as they are
    difficult to anticipate

*I don't know how to split my data into datasets.*

- Add note in documentation that it usually makes sense to create
  datasets on a per experiment basis as this allows the metadata to
  include experimental detail

*I want to update dataset manifests at the project level.*

- Add note to documentation explaining why this is a bad idea
- Give better error message when a user tries to do this

*Running manifest update on a directory with lots of files takes a long time.*

- Add note to documentation explaining why lots of small files cause problems
- Add note to documentation explaining that the problem can be overcome by tarring them
- Add validation step checking the numbers of files in the manifest root before
  with some meaningful feedback if there are lots of files present

*OSX generates .DStore files that get indexes in the manifest.*

- Brainstorm ways of implementing a .dtoolignore file

*Where can I access the features you demoed with datademo?*

- Brainstorm better name for functionality contained datademo
- Rename and release datademo
- Build datademo on cluster


Roadmap
-------

``dtoolcore``
~~~~~~~~~~~~~

- Remove libmagic dependence from dtoolcore this also has the benefit of
  making dtoolcore cross platform
- Brainstorm ways of implementing a .dtoolignore file


``dtoolutils``
--------------

- Investigate pure Python implementations of libmagic
- Implement helper function for creating mimetype overlays


``dtool``
---------

Features
~~~~~~~~

- Give better error message when a user tries to update manifests at a project level
- Make use of mimetype overlay in dtool
- Work out if we can remove project (and make collection fill that role more flexibly)
- Expose the ability to create collections to dtool
- Add ability to mark up a directory as a collection to dtool
- Add validation step checking the numbers of files in the manifest root before
  with some meaningful feedback if there are lots of files present

Documentation
~~~~~~~~~~~~~

- Write up reasoning why this is a bad idea including to keep code and data together
- Add note in documentation that it usually makes sense to create
  datasets on a per experiment basis as this allows the metadata to
  include experimental detail
- Add note to documentation explaining why lots of small files cause problems
- Add note to documentation explaining that the problem can be overcome by tarring them
- Add note to documentation explaining why this is a bad idea to update
  dataset manifests at the project level

``datademo``
------------

- Brainstorm better name for functionality contained datademo
- Refactor datademo to use dtoolcore
- Rename and release datademo
- Build datademo on cluster
