# Twitter_sentimental_analysis_pipeline -  Deployment with CICD Setup

A Twitter Sentiment analysis Project which will scrap twitter for the topic selected by the user. • The extracted tweets will then be used to determine the Sentiments of those tweets. • The different Visualizations will help us get a feel of the overall mood of the people on Twitter regarding the topic selected. • The Extracted Tweets data is first cleaned , filtered , unwanted words are deleted and the Sentiment Analysis is done on the clean data using the TextBlob Library.

Our Goal is to Create an API where the user will Enter a Topic, which we will search on Twitter and Extract tweets related to that Topic.
We will then do sentiment Analysis on the extracted tweets and classify them into Positive, Negative, Neutral.

Tools used here are Github , Jenkins , Ansible , Docker and Kubernetes. 

The following diagram represent the flow of the setup:

![tejas](https://user-images.githubusercontent.com/69673830/135084230-f794cf5b-745b-413e-9f14-985c11da0ae8.png)

Following steps were / should be followed to build this CICD setup. 

1. Setting up Kubernetes cluster anywhere were user desires it to be. Here AWS KOPS was used to deploy the cluster. 
link to deploy cluster using AWS KOPS: https://kubernetes.io/docs/setup/production-environment/tools/kops/
2. Two more clusters (Jenkins and Ansible) should be created. Docker can be installed on the Ansible server itself. 
3. The final setup of VMs in AWS would look like this:

![EC2 machines](https://user-images.githubusercontent.com/69673830/135087731-96d9c499-3a37-4fd6-9f97-b385c0f0e6d9.png)

4. SSH into Jenkins server , install Jenkins in it (https://pkg.jenkins.io/redhat-stable/) and download a plugin "Public_Over_SSH" from Manage Plugins.
5. Go into Configure systems and using "Add servers" option add two servers 

Name: Jenkins, Hostname: PrivateIp of the Jenkins server, Username: root and using password / key ensure connection is successful.

Name: Ansible, Hostname: PrivateIp of the Ansible server, Username: root and using password / key ensure connection is successful.

6. Ensure Password less authentication between Ansible server and Kubernetes master node / controller machine (controller machine should be accessible via SSH from Ansible server without password).
7. Ensure Password less authentication between Jenkins server and Ansible Server (Ansible server should be accessible via SSH from Jenkins server without password).
8. Install Docker in the Ansible server and login into Docker.
9. Install Ansible in the Ansible server. 
10. SSH into Ansible server and Run the following commands. 

```
cd /opt
vim ansible.yml 
```

11. And put the following script in the newly created ansible.yml (This would be our playbook).
```
- hosts: all
  become: true

  tasks:
  - name: delete deployment
    command: kubectl delete -f /opt/deployment.yml    
  - name: create deployment
    command: kubectl apply -f /opt/deployment.yml
  ```
  12. SSH into the controller machine and run the following commands. 
  ```
  cd /opt
  vim deployment.yml
  ```
  13. And put the following script in the newly created deployment.yml
```  
apiVersion: v1
kind: Service
metadata: 
  name: hello-python-service
spec:
  selector:
    app: hello-python
  ports:
  - protocol: "TCP"
    port: 80
    targetPort: 5000
    nodePort: 31200
  type: LoadBalancer


---

apiVersion: apps/v1
kind: Deployment
metadata: 
  name: hello-python
spec: 
  selector:
    matchLabels:
      app: hello-python
  replicas: 1
  template: 
    metadata:
      labels:
        app: hello-python
    spec:
      containers: 
      - name: hello-python
        image: tejasvishwasrao/trivagoproject  
        imagePullPolicy: Always 
        ports:
        - containerPort: 5000
``` 
Note: image: tejasvishwasrao/bigdataexam - here tejasvishwasrao refers to my personal dockerHub id and trivagoproject would be the image name.

14. SSH into Ansible server and add controller machines privateIp to the hosts folder, which can be found under the path /etc/ansible/hosts. 
15. SSH into jenkins server and install Git. 
16. Using webhook connect Github and our Jenkins server. 
17. Login int Jenkins and make a new Freestyle project with the name "trivagoproject" and make sure this name is same with the image name since it will be needed in the next steps during docker build.
18. Configure this project by selection "Git" under "Source Code Management"

![git 1](https://user-images.githubusercontent.com/69673830/135094340-bc7ecbbe-3620-40a8-b4e9-4a20db8ab42e.png)

19. Scrolling down to "Build Triggers" select "Github hook trigger for GITSCM polling"

![git 2](https://user-images.githubusercontent.com/69673830/135094636-058bbb7c-75df-4da4-9dd5-c17bce4fd417.png)

20. Scrolling down to "Build" select "Send files or execute commands over SSH" and under jenkins server run the following command:

```
rsync -avh /var/lib/jenkins/workspace/bigdataexam*  root@ANSIBLE_SERVER_PRIVATE_IP:/opt
````

21. Scroll down to "Add build step" select "Send files or execute commands over SSH" and under Ansible server run the following command:

```
cd /opt
docker image build -t $JOB_NAME:v1.$BUILD_ID .
docker image tag $JOB_NAME:v1.$BUILD_ID tejasvishwasrao/$JOB_NAME:v1.$BUILD_ID
docker image tag $JOB_NAME:v1.$BUILD_ID tejasvishwasrao/$JOB_NAME:latest
docker image push tejasvishwasrao/$JOB_NAME:v1.$BUILD_ID
docker image push tejasvishwasrao/$JOB_NAME:latest
docker image rmi $JOB_NAME:v1.$BUILD_ID tejasvishwasrao/$JOB_NAME:v1.$BUILD_ID tejasvishwasrao/$JOB_NAME:latest
```

22. Scroll down to "add post build action" and select "Send build artifacts over SSH" 

```
ansible-playbook  /opt/ansible.yml
````

23. Login into AWS and add rule to the Security group of the nodes by allowing the port 31200 since it is used in our service.
24. Run the pipeline manually first. 
Given below is the result after running pipeline manually.

![Capture](https://user-images.githubusercontent.com/69673830/158079520-ed778ea9-af4a-4c8e-9146-09b49c1ff075.PNG)

![Capture3](https://user-images.githubusercontent.com/69673830/158079863-b44b98c1-cf68-439a-8589-cf7bd7dd426c.PNG)

