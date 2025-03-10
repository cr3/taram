Technologies
============

Docker
------

`Docker`_ is used for ease of deployment, modularity, and
security. Here’s why:

* **Ease of Deployment & Portability**

  - Mail servers are complex, requiring multiple services (Postfix,
    Dovecot, Rspamd, ClamAV, etc.).
  - Docker Compose bundles everything into manageable containers.
  - Works consistently across different environments (Linux servers,
    cloud, VPS).

* **Modularity & Isolation**

  - Each service (Postfix, Dovecot, Rspamd, ClamAV, MySQL, etc.) runs
    in its own container.
  - If one component fails (e.g., Rspamd), others keep running.
  - Containers prevent dependency conflicts (e.g., different versions
    of OpenSSL, MySQL).

* **Security & Isolation**

  - Containers restrict services from accessing the host system directly.
  - Running in Docker minimizes risks compared to installing services
    directly.
  - Services have limited privileges and use internal Docker networks.

.. _Docker: https://www.docker.com/

React
-----

`React`_ is great for performance, modularity, and developer
experience. Here’s why:

* **Component-Based Architecture**

  - Reusable UI components = faster development & consistency.
  - Encourages separation of concerns (UI & logic stay organized).

* **Faster UI Updates with Virtual DOM**

  - React only updates what changes, making it more efficient than direct
    DOM manipulation.
  - Uses diffing algorithms to minimize UI re-renders.

* **Simpler State Management with React Hooks**

  - No need for complex class components - use hooks like useState,
    useEffect.
  - Hooks make state management easier compared to class-based lifecycle
    methods.

.. _React: https://react.dev/
