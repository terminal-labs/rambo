# Docker

At this time Docker is supported by using an intermediate host. The intermediate host is created with VirtualBox, and is the same OS as is used for the Docker container inside it. Setting both of those OSes to be the same avoids certain complexities and potential problems that would otherwise present.

Basic usage of Docker:

```
rambo up -p docker
rambo ssh
```
