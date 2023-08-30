# Chatbot Manifests

`Chatbot` can be deployed on kubernetes to reduce maintenance overhead while achieving horizontal scaling. Multiple approaches exist for deploying `Chatbot` on Kubernetes, including: 1. vanilla kubernetes deployment. 2. knative service deployment.

## Vanilla Kubernetes Deployment

The vanilla kubernetes deployment consists of a configmap, a deployment, a service and a virtual service. The benefit lies in its simplicity, sparing you the need to familiarize yourself with Knative. However, the primary drawback is its lack of automatic scaling in response to request rates.

Command used for vanilla kubernetes deployment:

```sh
kubectl kustomize manifests/overlays/istio | kubectl apply -f -
```

## Knative Service Deployment

The Knative Service deployment consists of a configmap and a `Service.serving.knative.dev`.

One of the notable benefits of Knative is its automatic scaling feature that adjusts the application based on request rates. This ensures that no pods are active during periods of no requests, while promptly scaling to multiple pods during periods of high request bursts. It can significantly reduce both your deployment resource usage and your expenses.

However, the trade-off is that it brings increased complexity and may require more time to grasp and effectively customize to suit your specific requirements. There are also certain considerations to keep in mind when deploying `Chatbot` as a Knative Service, which we will delve into further in the [caveats](#caveats) section.

Command used for knative deployment:

```sh
kubectl kustomize manifests/overlays/knative-serving | kubectl apply -f -
```

### Caveats

There are several important considerations to keep in mind when deploying `Chatbot` as a Knative Service.

If you choose to export `Chatbot` through the `config-domain` configmap, it will automatically expose `Chatbot` in the url form of `${app-name}.${namespace}.${your-domain}.${top-level-domain}`. This may look a bit wierd, but if this aligns with your specific use case, then you're all set. However, if your needs differ, you might need to expose `Chatbot` using a [custom domain](https://knative.dev/docs/serving/services/custom-domains/).

In the event that you're exposing `Chatbot` via a custom domain, be aware that it might not seamlessly support websockets. There are several known issues related to this:

- [Impossible to make websockets working on Knative with Google Cloud Run on GKE](https://github.com/knative/serving/issues/7933)
- [DomainMapping does not work with Websocket](https://github.com/knative/serving/issues/12601)
- [Websockets do not work with domainmapings by default](https://github.com/knative/serving/issues/13083)

## Third Party Dependenciess

### Redis

`Chatbot` employs Redis for the storage of messages and conversation entities.

For our Redis image, we've opted for [redis-stack](https://hub.docker.com/r/redis/redis-stack), given its potential applicability for similarity searches down the line.

This deployment involves a singular instance, with data persistence facilitated through a mounted volume.
