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

