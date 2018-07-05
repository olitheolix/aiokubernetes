The documentation is available (here)[https://aiokubernetes.readthedocs.io/en/latest/].

# Run Tests Locally
We use (Travis)[https://travis-ci.com/olitheolix/aiokubernetes] as our CI.

You can run the test locally use like Travis would:

```bash
   docker run -ti -v`pwd`:/src python:3.7-alpine3.7 /bin/ash -c "cd src; script/run-ci-tests.sh"
```
This will run all the tests in a dedicated Python container that has the
repository mapped into it.


![](https://cdn.pixabay.com/photo/2012/04/01/18/55/work-in-progress-24027_1280.png)
