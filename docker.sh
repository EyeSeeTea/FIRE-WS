rm firews.tar
tar cf firews.tar --owner=1000 --group=1000 fire fire-ws.conf migrations misc requirements.txt setup.py tests
docker build -t eyeseetea/firews .  || break
echo Running Tests...
docker run -i eyeseetea/firews .env/bin/python setup.py test
echo Starting Image...
docker run -d -p 5005:5000 eyeseetea/firews
echo Sample query...
sleep 5; curl -u joel:1 http://localhost:5005/currentUser
# don't forget to clean up:
# docker rm `docker ps -a -q`
# docker images
# docker rmi 
