# Item Catalog

> Gowri Prathap

## About the project

The Item Catalog project in Udacity Full stack developing course is about developing an application that provides a list of items with a variety of categories, as well as provide a user registration and authentication system. This project uses persistent data storage to create a RESTful web application that allows users to perform Create, Read, Update, and Delete operations.

A user does not need to be logged in in order to read the categories or items uploaded. However, users who created an item are the only users allowed to update or delete the item that they created. They cannot edit and delete items they did not create.

This program uses third-party auth with Google.


## Skills needed for this project
- Python
- HTML
- CSS
- Bootstrap
- Flask
- Jinja2
- SQLAchemy
- OAuth
- Google Login

## Prerequisites
- [Vagrant](https://www.vagrantup.com/)
- [Udacity Vagrantfile](https://github.com/udacity/fullstack-nanodegree-vm)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

## Getting Started

- Install Vagrant and VirtualBox
- Clone the Vagrantfile from the Udacity Repository
- Clone this repo into the `catalog/` directory found in the Vagrant directory
- Run `vagrant up` to run the virtual machine, then `vagrant ssh` to login to the VM
- run application with `python project.py` after going to the directory
- go to `http://localhost:5000` to access the application


## Running the tests

The endpoints can be acessible for all clients, but some pages is only available to logged users

### HTML Endpoints:

> * List all the categories in the database: `/category`
> * Create a new category in the database: `/category/news`
> * Edit a category in the database:     `/category/<int:category_id>/edit`
> * Delete a category in the database: `/category/<int:category_id>/delete`
> * List all items for the category:
> `/category/<int:category_id>/items`
> * Display an item in the category:
> `/category/<int:category_id>/items/<int:item_id>`
> * Add an item in the category: `/category/<int:category_id>/items/new`
> * Edit an item in the category:
> `/category/<int:category_id>/items/<int:item_id>/edit`
> * Delete an item in the category:
> `/category/<int:category_id>/items/<int:item_id>/delete`

### JSON Endpoints

> * List the categories with the itemss: `/category/JSON`
> * List the items of a particular category: `/category/<int:category_id>/items/JSON`
> * Display the information of each item: `/category/<int:category_id>/items/<int:item_id>/JSON`
