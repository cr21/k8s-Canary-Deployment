# k8s-Canary-Deployment


## Create EKS Cluster
```yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

iam:
  withOIDC: true

metadata:
  name: basic-cluster
  region: us-east-1
  version: "1.30"

managedNodeGroups:
  - name: ng-dedicated-1 # for pods with volumes
    instanceType: t3a.xlarge
    desiredCapacity: 1
    ssh:
      allow: true
      publicKeyPath: ~/.ssh/id_ed25519.pub
    iam:
      withAddonPolicies:
        autoScaler: true
        awsLoadBalancerController: true
        certManager: true
        externalDNS: true
        ebs: true
  - name: ng-spot-3
    # instanceSelector:
    #   memory: "16"
    #   vCPUs: 4
    instanceTypes:
    - t2.xlarge
    - t3.xlarge
    - t3a.xlarge
    desiredCapacity: 6
    spot: true
    labels:
      role: spot
    ssh:
      allow: true
      publicKeyPath: ~/.ssh/id_ed25519.pub
    iam:
      withAddonPolicies:
        autoScaler: true
        awsLoadBalancerController: true
        certManager: true
        externalDNS: true
        ebs: true

```

## Create EKS Cluster
```bash
eksctl create cluster -f eks-cluster.yaml
```

## KNative
 
### Install Knative and related components

```bash

kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.16.0/serving-crds.yaml
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.16.0/serving-core.yaml

kubectl apply -l knative.dev/crd-install=true -f https://github.com/knative/net-istio/releases/download/knative-v1.16.0/istio.yaml
kubectl apply -f https://github.com/knative/net-istio/releases/download/knative-v1.16.0/istio.yaml
kubectl apply -f https://github.com/knative/net-istio/releases/download/knative-v1.16.0/net-istio.yaml


kubectl --namespace istio-system get service istio-ingressgateway
kubectl get pods -n knative-serving



kubectl patch configmap/config-domain \
      --namespace knative-serving \
      --type merge \
      --patch '{"data":{"emlo.tsai":""}}'

kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.16.0/serving-hpa.yaml

kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.16.2/cert-manager.yaml


kubectl apply --server-side -f https://github.com/kserve/kserve/releases/download/v0.14.1/kserve.yaml



kubectl apply --server-side -f https://github.com/kserve/kserve/releases/download/v0.14.1/kserve.yaml

kubectl apply --server-side -f https://github.com/kserve/kserve/releases/download/v0.14.1/kserve-cluster-resources.yaml


eksctl create iamserviceaccount \
	--cluster=basic-cluster \
	--name=s3-read-only \
	--attach-policy-arn=arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess \
	--override-existing-serviceaccounts \
	--region us-east-1 \
	--approve

kubectl apply -f s3-secret.yaml

kubectl patch serviceaccount s3-read-only -p '{"secrets": [{"name": "s3-secret"}]}'

```


```bash
docker run -it --rm --shm-size=1g \
           --ulimit memlock=-1 \
           --ulimit stack=67108864 \
           -p 8085:8085 \
           --mount type=bind,source=/home/ubuntu/session-17/model-store/cat-classifier/model-store,target=/mnt/models/model-store \
           --mount type=bind,source=/home/ubuntu/session-17/model-store/cat-classifier/config,target=/mnt/models/config \
           -e TS_CONFIG_FILE=/mnt/models/config/config.properties \
           -e TS_DISABLE_TOKEN_AUTHORIZATION=true \
           pytorch/torchserve-kfs:0.12.0 \
           torchserve
```

```bash
kubectl apply -f vit-classifier.yaml
kubectl get pods
kubectl get inferenceservice
kubectl get pods
kubectl describe pod imagenet-vit-predictor-00001-deployment-cd85dc487-5zkm5 
kubectl logs imagenet-vit-predictor-00001-deployment-cd85dc487-5zkm5  -c storage-initializer
kubectl describe pod imagenet-vit-predictor-00001-deployment-cd85dc487-5zkm5 


❯ kubectl get inferenceservice
NAME           URL                                     READY   PREV   LATEST   PREVROLLEDOUTREVISION   LATESTREADYREVISION            AGE
imagenet-vit   http://imagenet-vit.default.emlo.tsai   True           100                              imagenet-vit-predictor-00001   4m57s


❯ kubectl get services  -n istio-system
NAME                    TYPE           CLUSTER-IP       EXTERNAL-IP                                                               PORT(S)                                      AGE
istio-ingressgateway    LoadBalancer   10.100.196.88    a7352fc5c5fd84b64a4381b964dcc123-1841539688.us-east-1.elb.amazonaws.com   15021:32538/TCP,80:32198/TCP,443:32150/TCP   133m
istiod                  ClusterIP      10.100.166.174   <none>                                                                    15010/TCP,15012/TCP,443/TCP,15014/TCP        133m
knative-local-gateway   ClusterIP      10.100.107.184   <none>                                                                    80/TCP,443/TCP  
```

```bash
❯ python3 send.py
{'content-length': '78', 'content-type': 'application/json', 'date': 'Sun, 16 Feb 2025 21:11:33 GMT', 'server': 'istio-envoy', 'x-envoy-upstream-service-time': '321'}
200
{'predictions': [{'class': 'tabby, tabby cat', 'probability': 0.484485000371933}]}
```

## Prometheus
```bash
git clone --branch release-0.14 <https://github.com/kserve/kserve.git
```

```bash
kubectl apply -f kserve/tools/monitoring/prometheus/prometheus.yaml
```



```bash
❯ touch qpext_image_patch.yaml
❯ kubectl patch configmaps -n knative-serving config-deployment --patch-file qpext_image_patch.yaml
configmap/config-deployment patched
```
## Grafana
```bash
## Grafana
```bash
# Add the Grafana Helm repository
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Create namespace and install Grafana
kubectl create namespace grafana
helm install grafana grafana/grafana --namespace grafana --version 8.8.4


kubectl get secret --namespace grafana grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo

kubectl port-forward svc/grafana --namespace grafana 3000:80

http://prometheus-operated.kfserving-monitoring.svc.cluster.local:9090
```
```

```bash
❯ python3 load.py
\nStarting load test at 2025-02-16 15:36:29
Total requests: 100
Concurrent requests: 30
--------------------------------------------------
\nLoad Test Results:
--------------------------------------------------
Total time: 26.08 seconds
Successful requests: 100
Failed requests: 0
Average response time: 6.597 seconds
Requests per second: 3.83
❯ kubectl get pods
NAME                                                       READY   STATUS            RESTARTS   AGE
imagenet-vit-predictor-00001-deployment-6849dbb468-24rdx   0/2     PodInitializing   0          35s
imagenet-vit-predictor-00001-deployment-6849dbb468-5mmfl   1/2     Running           0          34s
imagenet-vit-predictor-00001-deployment-6849dbb468-9ftvh   0/2     PodInitializing   0          33s
imagenet-vit-predictor-00001-deployment-6849dbb468-9n5h5   1/2     Running           0          35s
imagenet-vit-predictor-00001-deployment-6849dbb468-c4hwl   0/2     PodInitializing   0          35s
imagenet-vit-predictor-00001-deployment-6849dbb468-m6vmw   1/2     Terminating       0          5m27s
imagenet-vit-predictor-00001-deployment-6849dbb468-qxpf4   1/2     Terminating       0          2m59s
imagenet-vit-predictor-00001-deployment-6849dbb468-smrvl   1/2     Running           0          33s
imagenet-vit-predictor-00001-deployment-6849dbb468-t485q   0/2     PodInitializing   0          35s
imagenet-vit-predictor-00001-deployment-6849dbb468-w5cr4   0/2     PodInitializing   0          35s
imagenet-vit-predictor-00001-deployment-6849dbb468-wdww2   2/2     Running           0          2m59s
imagenet-vit-predictor-00001-deployment-6849dbb468-xc57k   0/2     PodInitializing   0          33s
```


```bash
❯ kubectl get pods
NAME                                                       READY   STATUS        RESTARTS   AGE
imagenet-vit-predictor-00001-deployment-6849dbb468-24rdx   1/2     Terminating   0          2m20s
imagenet-vit-predictor-00001-deployment-6849dbb468-5mmfl   1/2     Terminating   0          2m19s
imagenet-vit-predictor-00001-deployment-6849dbb468-7c9k6   0/2     Pending       0          14s
imagenet-vit-predictor-00001-deployment-6849dbb468-7db6h   1/2     Running       0          20s
imagenet-vit-predictor-00001-deployment-6849dbb468-9ftvh   1/2     Terminating   0          2m18s
imagenet-vit-predictor-00001-deployment-6849dbb468-9n5h5   1/2     Terminating   0          2m20s
imagenet-vit-predictor-00001-deployment-6849dbb468-blnmr   1/2     Running       0          21s
imagenet-vit-predictor-00001-deployment-6849dbb468-c4hwl   1/2     Terminating   0          2m20s
imagenet-vit-predictor-00001-deployment-6849dbb468-cfcqr   1/2     Running       0          20s
imagenet-vit-predictor-00001-deployment-6849dbb468-dv4r9   0/2     Pending       0          18s
imagenet-vit-predictor-00001-deployment-6849dbb468-m6vmw   1/2     Terminating   0          7m12s
imagenet-vit-predictor-00001-deployment-6849dbb468-ndtm9   0/2     Pending       0          14s
imagenet-vit-predictor-00001-deployment-6849dbb468-qxpf4   1/2     Terminating   0          4m44s
imagenet-vit-predictor-00001-deployment-6849dbb468-sk7xf   1/2     Running       0          21s
imagenet-vit-predictor-00001-deployment-6849dbb468-smrvl   1/2     Terminating   0          2m18s
imagenet-vit-predictor-00001-deployment-6849dbb468-t485q   1/2     Terminating   0          2m20s
imagenet-vit-predictor-00001-deployment-6849dbb468-tds28   0/2     Pending       0          18s
imagenet-vit-predictor-00001-deployment-6849dbb468-w5cr4   1/2     Terminating   0          2m20s
imagenet-vit-predictor-00001-deployment-6849dbb468-wdww2   1/2     Terminating   0          4m44s
imagenet-vit-predictor-00001-deployment-6849dbb468-xc57k   1/2     Terminating   0          2m18s


❯ python3 load.py --total-requests 300 --concurrent-requests 5
\nStarting load test at 2025-02-16 15:38:28
Total requests: 300
Concurrent requests: 5
--------------------------------------------------
\nLoad Test Results:
--------------------------------------------------
Total time: 150.41 seconds
Successful requests: 295
Failed requests: 5
Average response time: 2.497 seconds
Requests per second: 1.99
```


### Canary Deployment
```yaml

apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: "imagenet-vit"
  annotations:
    serving.kserve.io/enable-metric-aggregation: "true"
    serving.kserve.io/enable-prometheus-scraping: "true"
    autoscaling.knative.dev/target: "1"
spec:
  predictor:
    minReplicas: 0
    maxReplicas: 10
    containerConcurrency: 10
    canaryTrafficPercent: 10
    serviceAccountName: s3-read-only
    pytorch:
      protocolVersion: v1
      # storageUri: s3://cr-tsai-emlo/kserve-ig/imagenet-vit/
      storageUri: s3://cr-tsai-emlo/kserve-ig/cat-classifier/
      image: pytorch/torchserve-kfs:0.12.0
      resources:
        limits:
          cpu: 2600m
          memory: 4Gi
      env:
        - name: TS_DISABLE_TOKEN_AUTHORIZATION
          value: "true"

```
```bash
kubectl apply -f vit-classifier.yaml
```

```bash
❯ kubectl get inferenceservice
NAME           URL                                     READY   PREV   LATEST   PREVROLLEDOUTREVISION          LATESTREADYREVISION            AGE
imagenet-vit   http://imagenet-vit.default.emlo.tsai   True    70     30       imagenet-vit-predictor-00001   imagenet-vit-predictor-00004   36m



❯ kubectl get pods
NAME                                                       READY   STATUS     RESTARTS   AGE
imagenet-vit-predictor-00001-deployment-6849dbb468-4j2fw   1/2     Running    0          22s
imagenet-vit-predictor-00001-deployment-6849dbb468-5998n   2/2     Running    0          82s
imagenet-vit-predictor-00001-deployment-6849dbb468-5pkcg   1/2     Running    0          78s
imagenet-vit-predictor-00001-deployment-6849dbb468-6xr9s   1/2     Running    0          22s
imagenet-vit-predictor-00001-deployment-6849dbb468-b9kzz   1/2     Running    0          76s
imagenet-vit-predictor-00001-deployment-6849dbb468-bvkrh   1/2     Running    0          80s
imagenet-vit-predictor-00001-deployment-6849dbb468-ft4w6   2/2     Running    0          82s
imagenet-vit-predictor-00001-deployment-6849dbb468-gqbn9   2/2     Running    0          84s
imagenet-vit-predictor-00001-deployment-6849dbb468-qqqmv   2/2     Running    0          84s
imagenet-vit-predictor-00001-deployment-6849dbb468-wsgzd   2/2     Running    0          82s
imagenet-vit-predictor-00004-deployment-7d9766c646-7c5j5   0/2     Init:0/1   0          1s
imagenet-vit-predictor-00004-deployment-7d9766c646-k9t87   2/2     Running    0          3m3s


❯ kubectl get inferenceservice
NAME           URL                                     READY   PREV   LATEST   PREVROLLEDOUTREVISION          LATESTREADYREVISION            AGE
imagenet-vit   http://imagenet-vit.default.emlo.tsai   True    70     30       imagenet-vit-predictor-00001   imagenet-vit-predictor-00004   38m

```


## ARGO CD

```bash
kubectl create namespace argocd

❯ kubectl create namespace argocd
namespace/argocd created
```

```bash
❯ kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
customresourcedefinition.apiextensions.k8s.io/applications.argoproj.io created
customresourcedefinition.apiextensions.k8s.io/applicationsets.argoproj.io created
customresourcedefinition.apiextensions.k8s.io/appprojects.argoproj.io created
serviceaccount/argocd-application-controller created
serviceaccount/argocd-applicationset-controller created
serviceaccount/argocd-dex-server created
serviceaccount/argocd-notifications-controller created
serviceaccount/argocd-redis created
serviceaccount/argocd-repo-server created
serviceaccount/argocd-server created
role.rbac.authorization.k8s.io/argocd-application-controller created
role.rbac.authorization.k8s.io/argocd-applicationset-controller created
role.rbac.authorization.k8s.io/argocd-dex-server created
role.rbac.authorization.k8s.io/argocd-notifications-controller created
role.rbac.authorization.k8s.io/argocd-redis created
role.rbac.authorization.k8s.io/argocd-server created
clusterrole.rbac.authorization.k8s.io/argocd-application-controller created
clusterrole.rbac.authorization.k8s.io/argocd-applicationset-controller created
clusterrole.rbac.authorization.k8s.io/argocd-server created
rolebinding.rbac.authorization.k8s.io/argocd-application-controller created
rolebinding.rbac.authorization.k8s.io/argocd-applicationset-controller created
rolebinding.rbac.authorization.k8s.io/argocd-dex-server created
rolebinding.rbac.authorization.k8s.io/argocd-notifications-controller created
rolebinding.rbac.authorization.k8s.io/argocd-redis created
rolebinding.rbac.authorization.k8s.io/argocd-server created
clusterrolebinding.rbac.authorization.k8s.io/argocd-application-controller created
clusterrolebinding.rbac.authorization.k8s.io/argocd-applicationset-controller created
clusterrolebinding.rbac.authorization.k8s.io/argocd-server created
configmap/argocd-cm created
configmap/argocd-cmd-params-cm created
configmap/argocd-gpg-keys-cm created
configmap/argocd-notifications-cm created
configmap/argocd-rbac-cm created
configmap/argocd-ssh-known-hosts-cm created
configmap/argocd-tls-certs-cm created
secret/argocd-notifications-secret created
secret/argocd-secret created
service/argocd-applicationset-controller created
service/argocd-dex-server created
service/argocd-metrics created
service/argocd-notifications-controller-metrics created
service/argocd-redis created
service/argocd-repo-server created
service/argocd-server created
service/argocd-server-metrics created
deployment.apps/argocd-applicationset-controller created
deployment.apps/argocd-dex-server created
deployment.apps/argocd-notifications-controller created
deployment.apps/argocd-redis created
deployment.apps/argocd-repo-server created
deployment.apps/argocd-server created
statefulset.apps/argocd-application-controller created
networkpolicy.networking.k8s.io/argocd-application-controller-network-policy created
networkpolicy.networking.k8s.io/argocd-applicationset-controller-network-policy created
networkpolicy.networking.k8s.io/argocd-dex-server-network-policy created
networkpolicy.networking.k8s.io/argocd-notifications-controller-network-policy created
networkpolicy.networking.k8s.io/argocd-redis-network-policy created
networkpolicy.networking.k8s.io/argocd-repo-server-network-policy created
networkpolicy.networking.k8s.io/argocd-server-network-policy created
```

```bash

❯ kubectl get pods -n argocd
NAME                                                READY   STATUS    RESTARTS   AGE
argocd-application-controller-0                     1/1     Running   0          94s
argocd-applicationset-controller-5ccf6c6796-2lxb6   1/1     Running   0          96s
argocd-dex-server-64c4b76d7d-r8jdt                  1/1     Running   0          95s
argocd-notifications-controller-cf6b86bb9-sdgx5     1/1     Running   0          95s
argocd-redis-5bc87d6645-7nwbc                       1/1     Running   0          95s
argocd-repo-server-64cd4955b8-t2h2v                 1/1     Running   0          95s
argocd-server-848df88f96-nw2tq 


argocd admin initial-password -n argocd
W1JtZsSbArV4DqA8

```

```bash
❯ kubectl get pods
NAME                                                          READY   STATUS    RESTARTS   AGE
cat-classifier-predictor-00001-deployment-8665d9c564-dzbvt    1/2     Running   0          51s
food-classifier-predictor-00001-deployment-7c6c4b548d-zjftv   1/2     Running   0          51s
imagenet-vit-predictor-00004-deployment-7d9766c646-k9t87      2/2     Running   0          79m


❯ kubectl get inferenceservice
NAME              URL                                     READY     PREV   LATEST   PREVROLLEDOUTREVISION          LATESTREADYREVISION            AGE
cat-classifier                                            Unknown                                                                                 77s
food-classifier                                           Unknown                                                                                 77s
imagenet-vit      http://imagenet-vit.default.emlo.tsai   True      70     30       imagenet-vit-predictor-00001   imagenet-vit-predictor-00004   113m



❯ python3 send.py
{'content-length': '71', 'content-type': 'application/json', 'date': 'Sun, 16 Feb 2025 23:33:33 GMT', 'server': 'istio-envoy', 'x-envoy-upstream-service-time': '282'}
200
{'predictions': [{'class': 'miso_soup', 'probability': 0.630021870136261}]}
```

### ADD new deployment to Argo CD

1. Add new deployment yaml file to model-deployments folder
2. commit and push to github
3. Argo CD will detect the new deployment and create a new application

```bash

❯ kubectl get pods
NAME                                                          READY   STATUS        RESTARTS   AGE
dog-classifier-predictor-00001-deployment-5464f9fc6d-8pzc4    1/2     Running       0          58s
food-classifier-predictor-00001-deployment-7c6c4b548d-h8ft8   1/2     Terminating   0          6m40s
imagenet-vit-predictor-00004-deployment-7d9766c646-k9t87      2/2     Running       0          92m


❯ kubectl get inferenceservice
NAME              URL                                        READY   PREV   LATEST   PREVROLLEDOUTREVISION          LATESTREADYREVISION               AGE
cat-classifier    http://cat-classifier.default.emlo.tsai    True           100                                     cat-classifier-predictor-00001    16m
dog-classifier    http://dog-classifier.default.emlo.tsai    True           100                                     dog-classifier-predictor-00001    3m45s
food-classifier   http://food-classifier.default.emlo.tsai   True           100                                     food-classifier-predictor-00001   16m
imagenet-vit      http://imagenet-vit.default.emlo.tsai      True    70     30       imagenet-vit-predictor-00001   imagenet-vit-predictor-00004      129m
```

```bash
❯ python3 send.py
{'content-length': '83', 'content-type': 'application/json', 'date': 'Mon, 17 Feb 2025 00:05:55 GMT', 'server': 'istio-envoy', 'x-envoy-upstream-service-time': '287'}
200
{'predictions': [{'class': 'Domestic Short Hair', 'probability': 0.27160829305648804}]}


❯ kubectl get pods
NAME                                                         READY   STATUS        RESTARTS   AGE
cat-classifier-predictor-00001-deployment-8665d9c564-4gbcr   2/2     Running       0          2m16s
cat-classifier-predictor-00001-deployment-8665d9c564-tr52h   2/2     Running       0          2m16s
dog-classifier-predictor-00001-deployment-5464f9fc6d-c2mhq   1/2     Terminating   0          4m32s
dog-classifier-predictor-00001-deployment-5464f9fc6d-hp8kt   1/2     Terminating   0          4m32s
imagenet-vit-predictor-00004-deployment-7d9766c646-k9t87     2/2     Running       0          121m
```