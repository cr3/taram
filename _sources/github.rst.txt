GitHub
======

Generate SSH key
----------------

An SSH key is needed to communicate securely between GitHub and the
server, in both directions. To keep things simple, generate an RSA key
on the server:

.. code-block:: console

  ssh-keygen -t rsa -b 4096

Connect GitHub to server
------------------------

GitHub needs to connect to the deploy server where it can deploy the code merged
in the repository. First, authorize GitHub to connect to the server by
appending the public key to the authorized keys on the server:

.. code-block:: console

  cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

Then, configure the repository secrets with the private key and other
details about the server:

* SSH_PRIVATE_KEY: content of the `taram_rsa` file
* SSH_USER: user name to access the server
* SSH_HOST: hostname/ip-address of your server
* WORK_DIR: path to the directory containing the repository
* MAIN_BRANCH: name of the main branch (mostly main)

Connect server to GitHub
------------------------

In turn, the server also needs to connect to GitHub where it can pull the
latest code. In GitHub, configure the account of the GitHub user with the
private key from the ``~/.ssh/id_rsa.pub`` file on the server.
