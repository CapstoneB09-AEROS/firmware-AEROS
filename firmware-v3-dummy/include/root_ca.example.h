#pragma once
// Copy to root_ca.h and supply the CA certificate that validates YOUR HiveMQ
// endpoint. Get the PEM from a trusted CA source and verify its chain.
// Never bypass TLS with setInsecure().
static const char ROOT_CA[] = "";
