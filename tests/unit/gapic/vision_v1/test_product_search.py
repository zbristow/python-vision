# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import mock

import grpc
from grpc.experimental import aio
import math
import pytest
from proto.marshal.rules.dates import DurationRule, TimestampRule

from google import auth
from google.api_core import client_options
from google.api_core import exceptions
from google.api_core import future
from google.api_core import gapic_v1
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.api_core import operation_async
from google.api_core import operations_v1
from google.auth import credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.vision_v1.services.product_search import ProductSearchAsyncClient
from google.cloud.vision_v1.services.product_search import ProductSearchClient
from google.cloud.vision_v1.services.product_search import pagers
from google.cloud.vision_v1.services.product_search import transports
from google.cloud.vision_v1.types import geometry
from google.cloud.vision_v1.types import product_search_service
from google.longrunning import operations_pb2
from google.oauth2 import service_account
from google.protobuf import any_pb2 as any  # type: ignore
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore
from google.rpc import status_pb2 as status  # type: ignore


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"


# If default endpoint is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint(client):
    return (
        "foo.googleapis.com"
        if ("localhost" in client.DEFAULT_ENDPOINT)
        else client.DEFAULT_ENDPOINT
    )


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert ProductSearchClient._get_default_mtls_endpoint(None) is None
    assert (
        ProductSearchClient._get_default_mtls_endpoint(api_endpoint)
        == api_mtls_endpoint
    )
    assert (
        ProductSearchClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        ProductSearchClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        ProductSearchClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        ProductSearchClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi
    )


@pytest.mark.parametrize(
    "client_class", [ProductSearchClient, ProductSearchAsyncClient]
)
def test_product_search_client_from_service_account_file(client_class):
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file("dummy/file/path.json")
        assert client._transport._credentials == creds

        client = client_class.from_service_account_json("dummy/file/path.json")
        assert client._transport._credentials == creds

        assert client._transport._host == "vision.googleapis.com:443"


def test_product_search_client_get_transport_class():
    transport = ProductSearchClient.get_transport_class()
    assert transport == transports.ProductSearchGrpcTransport

    transport = ProductSearchClient.get_transport_class("grpc")
    assert transport == transports.ProductSearchGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (ProductSearchClient, transports.ProductSearchGrpcTransport, "grpc"),
        (
            ProductSearchAsyncClient,
            transports.ProductSearchGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
@mock.patch.object(
    ProductSearchClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(ProductSearchClient),
)
@mock.patch.object(
    ProductSearchAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(ProductSearchAsyncClient),
)
def test_product_search_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(ProductSearchClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(ProductSearchClient, "get_transport_class") as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            api_mtls_endpoint="squid.clam.whelk",
            client_cert_source=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS is
    # "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "never"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                api_mtls_endpoint=client.DEFAULT_ENDPOINT,
                client_cert_source=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS is
    # "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "always"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                api_mtls_endpoint=client.DEFAULT_MTLS_ENDPOINT,
                client_cert_source=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided, GOOGLE_API_USE_MTLS is
    # "auto", and client_cert_source is provided.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "auto"}):
        options = client_options.ClientOptions(
            client_cert_source=client_cert_source_callback
        )
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(client_options=options)
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                api_mtls_endpoint=client.DEFAULT_MTLS_ENDPOINT,
                client_cert_source=client_cert_source_callback,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided, GOOGLE_API_USE_MTLS is
    # "auto", and default_client_cert_source is provided.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "auto"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=True,
            ):
                patched.return_value = None
                client = client_class()
                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=client.DEFAULT_MTLS_ENDPOINT,
                    scopes=None,
                    api_mtls_endpoint=client.DEFAULT_MTLS_ENDPOINT,
                    client_cert_source=None,
                    quota_project_id=None,
                    client_info=transports.base.DEFAULT_CLIENT_INFO,
                )

    # Check the case api_endpoint is not provided, GOOGLE_API_USE_MTLS is
    # "auto", but client_cert_source and default_client_cert_source are None.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "auto"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=False,
            ):
                patched.return_value = None
                client = client_class()
                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=client.DEFAULT_ENDPOINT,
                    scopes=None,
                    api_mtls_endpoint=client.DEFAULT_ENDPOINT,
                    client_cert_source=None,
                    quota_project_id=None,
                    client_info=transports.base.DEFAULT_CLIENT_INFO,
                )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError):
            client = client_class()

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            api_mtls_endpoint=client.DEFAULT_ENDPOINT,
            client_cert_source=None,
            quota_project_id="octopus",
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (ProductSearchClient, transports.ProductSearchGrpcTransport, "grpc"),
        (
            ProductSearchAsyncClient,
            transports.ProductSearchGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_product_search_client_client_options_scopes(
    client_class, transport_class, transport_name
):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(scopes=["1", "2"],)
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=["1", "2"],
            api_mtls_endpoint=client.DEFAULT_ENDPOINT,
            client_cert_source=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (ProductSearchClient, transports.ProductSearchGrpcTransport, "grpc"),
        (
            ProductSearchAsyncClient,
            transports.ProductSearchGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_product_search_client_client_options_credentials_file(
    client_class, transport_class, transport_name
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            api_mtls_endpoint=client.DEFAULT_ENDPOINT,
            client_cert_source=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_product_search_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.vision_v1.services.product_search.transports.ProductSearchGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = ProductSearchClient(
            client_options={"api_endpoint": "squid.clam.whelk"}
        )
        grpc_transport.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            api_mtls_endpoint="squid.clam.whelk",
            client_cert_source=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_create_product_set(
    transport: str = "grpc", request_type=product_search_service.CreateProductSetRequest
):
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ProductSet(
            name="name_value", display_name="display_name_value",
        )

        response = client.create_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == product_search_service.CreateProductSetRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, product_search_service.ProductSet)

    assert response.name == "name_value"

    assert response.display_name == "display_name_value"


def test_create_product_set_from_dict():
    test_create_product_set(request_type=dict)


@pytest.mark.asyncio
async def test_create_product_set_async(transport: str = "grpc_asyncio"):
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = product_search_service.CreateProductSetRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ProductSet(
                name="name_value", display_name="display_name_value",
            )
        )

        response = await client.create_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, product_search_service.ProductSet)

    assert response.name == "name_value"

    assert response.display_name == "display_name_value"


def test_create_product_set_field_headers():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.CreateProductSetRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_product_set), "__call__"
    ) as call:
        call.return_value = product_search_service.ProductSet()

        client.create_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_product_set_field_headers_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.CreateProductSetRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_product_set), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ProductSet()
        )

        await client.create_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_product_set_flattened():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ProductSet()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_product_set(
            parent="parent_value",
            product_set=product_search_service.ProductSet(name="name_value"),
            product_set_id="product_set_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].product_set == product_search_service.ProductSet(
            name="name_value"
        )

        assert args[0].product_set_id == "product_set_id_value"


def test_create_product_set_flattened_error():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_product_set(
            product_search_service.CreateProductSetRequest(),
            parent="parent_value",
            product_set=product_search_service.ProductSet(name="name_value"),
            product_set_id="product_set_id_value",
        )


@pytest.mark.asyncio
async def test_create_product_set_flattened_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ProductSet()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ProductSet()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_product_set(
            parent="parent_value",
            product_set=product_search_service.ProductSet(name="name_value"),
            product_set_id="product_set_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].product_set == product_search_service.ProductSet(
            name="name_value"
        )

        assert args[0].product_set_id == "product_set_id_value"


@pytest.mark.asyncio
async def test_create_product_set_flattened_error_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_product_set(
            product_search_service.CreateProductSetRequest(),
            parent="parent_value",
            product_set=product_search_service.ProductSet(name="name_value"),
            product_set_id="product_set_id_value",
        )


def test_list_product_sets(
    transport: str = "grpc", request_type=product_search_service.ListProductSetsRequest
):
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_product_sets), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ListProductSetsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_product_sets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == product_search_service.ListProductSetsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListProductSetsPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_product_sets_from_dict():
    test_list_product_sets(request_type=dict)


@pytest.mark.asyncio
async def test_list_product_sets_async(transport: str = "grpc_asyncio"):
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = product_search_service.ListProductSetsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_product_sets), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ListProductSetsResponse(
                next_page_token="next_page_token_value",
            )
        )

        response = await client.list_product_sets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListProductSetsAsyncPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_product_sets_field_headers():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.ListProductSetsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_product_sets), "__call__"
    ) as call:
        call.return_value = product_search_service.ListProductSetsResponse()

        client.list_product_sets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_product_sets_field_headers_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.ListProductSetsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_product_sets), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ListProductSetsResponse()
        )

        await client.list_product_sets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_product_sets_flattened():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_product_sets), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ListProductSetsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_product_sets(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


def test_list_product_sets_flattened_error():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_product_sets(
            product_search_service.ListProductSetsRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_product_sets_flattened_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_product_sets), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ListProductSetsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ListProductSetsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_product_sets(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_product_sets_flattened_error_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_product_sets(
            product_search_service.ListProductSetsRequest(), parent="parent_value",
        )


def test_list_product_sets_pager():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_product_sets), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            product_search_service.ListProductSetsResponse(
                product_sets=[
                    product_search_service.ProductSet(),
                    product_search_service.ProductSet(),
                    product_search_service.ProductSet(),
                ],
                next_page_token="abc",
            ),
            product_search_service.ListProductSetsResponse(
                product_sets=[], next_page_token="def",
            ),
            product_search_service.ListProductSetsResponse(
                product_sets=[product_search_service.ProductSet(),],
                next_page_token="ghi",
            ),
            product_search_service.ListProductSetsResponse(
                product_sets=[
                    product_search_service.ProductSet(),
                    product_search_service.ProductSet(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_product_sets(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, product_search_service.ProductSet) for i in results)


def test_list_product_sets_pages():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_product_sets), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            product_search_service.ListProductSetsResponse(
                product_sets=[
                    product_search_service.ProductSet(),
                    product_search_service.ProductSet(),
                    product_search_service.ProductSet(),
                ],
                next_page_token="abc",
            ),
            product_search_service.ListProductSetsResponse(
                product_sets=[], next_page_token="def",
            ),
            product_search_service.ListProductSetsResponse(
                product_sets=[product_search_service.ProductSet(),],
                next_page_token="ghi",
            ),
            product_search_service.ListProductSetsResponse(
                product_sets=[
                    product_search_service.ProductSet(),
                    product_search_service.ProductSet(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_product_sets(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_product_sets_async_pager():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_product_sets),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            product_search_service.ListProductSetsResponse(
                product_sets=[
                    product_search_service.ProductSet(),
                    product_search_service.ProductSet(),
                    product_search_service.ProductSet(),
                ],
                next_page_token="abc",
            ),
            product_search_service.ListProductSetsResponse(
                product_sets=[], next_page_token="def",
            ),
            product_search_service.ListProductSetsResponse(
                product_sets=[product_search_service.ProductSet(),],
                next_page_token="ghi",
            ),
            product_search_service.ListProductSetsResponse(
                product_sets=[
                    product_search_service.ProductSet(),
                    product_search_service.ProductSet(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_product_sets(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, product_search_service.ProductSet) for i in responses)


@pytest.mark.asyncio
async def test_list_product_sets_async_pages():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_product_sets),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            product_search_service.ListProductSetsResponse(
                product_sets=[
                    product_search_service.ProductSet(),
                    product_search_service.ProductSet(),
                    product_search_service.ProductSet(),
                ],
                next_page_token="abc",
            ),
            product_search_service.ListProductSetsResponse(
                product_sets=[], next_page_token="def",
            ),
            product_search_service.ListProductSetsResponse(
                product_sets=[product_search_service.ProductSet(),],
                next_page_token="ghi",
            ),
            product_search_service.ListProductSetsResponse(
                product_sets=[
                    product_search_service.ProductSet(),
                    product_search_service.ProductSet(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_product_sets(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_get_product_set(
    transport: str = "grpc", request_type=product_search_service.GetProductSetRequest
):
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_product_set), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ProductSet(
            name="name_value", display_name="display_name_value",
        )

        response = client.get_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == product_search_service.GetProductSetRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, product_search_service.ProductSet)

    assert response.name == "name_value"

    assert response.display_name == "display_name_value"


def test_get_product_set_from_dict():
    test_get_product_set(request_type=dict)


@pytest.mark.asyncio
async def test_get_product_set_async(transport: str = "grpc_asyncio"):
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = product_search_service.GetProductSetRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ProductSet(
                name="name_value", display_name="display_name_value",
            )
        )

        response = await client.get_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, product_search_service.ProductSet)

    assert response.name == "name_value"

    assert response.display_name == "display_name_value"


def test_get_product_set_field_headers():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.GetProductSetRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_product_set), "__call__") as call:
        call.return_value = product_search_service.ProductSet()

        client.get_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_product_set_field_headers_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.GetProductSetRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_product_set), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ProductSet()
        )

        await client.get_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_product_set_flattened():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_product_set), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ProductSet()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_product_set(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_get_product_set_flattened_error():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_product_set(
            product_search_service.GetProductSetRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_product_set_flattened_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ProductSet()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ProductSet()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_product_set(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_product_set_flattened_error_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_product_set(
            product_search_service.GetProductSetRequest(), name="name_value",
        )


def test_update_product_set(
    transport: str = "grpc", request_type=product_search_service.UpdateProductSetRequest
):
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.update_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ProductSet(
            name="name_value", display_name="display_name_value",
        )

        response = client.update_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == product_search_service.UpdateProductSetRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, product_search_service.ProductSet)

    assert response.name == "name_value"

    assert response.display_name == "display_name_value"


def test_update_product_set_from_dict():
    test_update_product_set(request_type=dict)


@pytest.mark.asyncio
async def test_update_product_set_async(transport: str = "grpc_asyncio"):
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = product_search_service.UpdateProductSetRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ProductSet(
                name="name_value", display_name="display_name_value",
            )
        )

        response = await client.update_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, product_search_service.ProductSet)

    assert response.name == "name_value"

    assert response.display_name == "display_name_value"


def test_update_product_set_field_headers():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.UpdateProductSetRequest()
    request.product_set.name = "product_set.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.update_product_set), "__call__"
    ) as call:
        call.return_value = product_search_service.ProductSet()

        client.update_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "product_set.name=product_set.name/value",) in kw[
        "metadata"
    ]


@pytest.mark.asyncio
async def test_update_product_set_field_headers_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.UpdateProductSetRequest()
    request.product_set.name = "product_set.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_product_set), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ProductSet()
        )

        await client.update_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "product_set.name=product_set.name/value",) in kw[
        "metadata"
    ]


def test_update_product_set_flattened():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.update_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ProductSet()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_product_set(
            product_set=product_search_service.ProductSet(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].product_set == product_search_service.ProductSet(
            name="name_value"
        )

        assert args[0].update_mask == field_mask.FieldMask(paths=["paths_value"])


def test_update_product_set_flattened_error():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_product_set(
            product_search_service.UpdateProductSetRequest(),
            product_set=product_search_service.ProductSet(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_product_set_flattened_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ProductSet()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ProductSet()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_product_set(
            product_set=product_search_service.ProductSet(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].product_set == product_search_service.ProductSet(
            name="name_value"
        )

        assert args[0].update_mask == field_mask.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_product_set_flattened_error_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_product_set(
            product_search_service.UpdateProductSetRequest(),
            product_set=product_search_service.ProductSet(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )


def test_delete_product_set(
    transport: str = "grpc", request_type=product_search_service.DeleteProductSetRequest
):
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.delete_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == product_search_service.DeleteProductSetRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_product_set_from_dict():
    test_delete_product_set(request_type=dict)


@pytest.mark.asyncio
async def test_delete_product_set_async(transport: str = "grpc_asyncio"):
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = product_search_service.DeleteProductSetRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        response = await client.delete_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_product_set_field_headers():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.DeleteProductSetRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_product_set), "__call__"
    ) as call:
        call.return_value = None

        client.delete_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_product_set_field_headers_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.DeleteProductSetRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_product_set), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        await client.delete_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_product_set_flattened():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_product_set(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_delete_product_set_flattened_error():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_product_set(
            product_search_service.DeleteProductSetRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_product_set_flattened_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_product_set(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_product_set_flattened_error_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_product_set(
            product_search_service.DeleteProductSetRequest(), name="name_value",
        )


def test_create_product(
    transport: str = "grpc", request_type=product_search_service.CreateProductRequest
):
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_product), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.Product(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            product_category="product_category_value",
        )

        response = client.create_product(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == product_search_service.CreateProductRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, product_search_service.Product)

    assert response.name == "name_value"

    assert response.display_name == "display_name_value"

    assert response.description == "description_value"

    assert response.product_category == "product_category_value"


def test_create_product_from_dict():
    test_create_product(request_type=dict)


@pytest.mark.asyncio
async def test_create_product_async(transport: str = "grpc_asyncio"):
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = product_search_service.CreateProductRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_product), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.Product(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                product_category="product_category_value",
            )
        )

        response = await client.create_product(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, product_search_service.Product)

    assert response.name == "name_value"

    assert response.display_name == "display_name_value"

    assert response.description == "description_value"

    assert response.product_category == "product_category_value"


def test_create_product_field_headers():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.CreateProductRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_product), "__call__") as call:
        call.return_value = product_search_service.Product()

        client.create_product(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_product_field_headers_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.CreateProductRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_product), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.Product()
        )

        await client.create_product(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_product_flattened():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_product), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.Product()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_product(
            parent="parent_value",
            product=product_search_service.Product(name="name_value"),
            product_id="product_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].product == product_search_service.Product(name="name_value")

        assert args[0].product_id == "product_id_value"


def test_create_product_flattened_error():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_product(
            product_search_service.CreateProductRequest(),
            parent="parent_value",
            product=product_search_service.Product(name="name_value"),
            product_id="product_id_value",
        )


@pytest.mark.asyncio
async def test_create_product_flattened_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_product), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.Product()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.Product()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_product(
            parent="parent_value",
            product=product_search_service.Product(name="name_value"),
            product_id="product_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].product == product_search_service.Product(name="name_value")

        assert args[0].product_id == "product_id_value"


@pytest.mark.asyncio
async def test_create_product_flattened_error_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_product(
            product_search_service.CreateProductRequest(),
            parent="parent_value",
            product=product_search_service.Product(name="name_value"),
            product_id="product_id_value",
        )


def test_list_products(
    transport: str = "grpc", request_type=product_search_service.ListProductsRequest
):
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_products), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ListProductsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_products(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == product_search_service.ListProductsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListProductsPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_products_from_dict():
    test_list_products(request_type=dict)


@pytest.mark.asyncio
async def test_list_products_async(transport: str = "grpc_asyncio"):
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = product_search_service.ListProductsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_products), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ListProductsResponse(
                next_page_token="next_page_token_value",
            )
        )

        response = await client.list_products(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListProductsAsyncPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_products_field_headers():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.ListProductsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_products), "__call__") as call:
        call.return_value = product_search_service.ListProductsResponse()

        client.list_products(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_products_field_headers_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.ListProductsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_products), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ListProductsResponse()
        )

        await client.list_products(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_products_flattened():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_products), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ListProductsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_products(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


def test_list_products_flattened_error():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_products(
            product_search_service.ListProductsRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_products_flattened_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_products), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ListProductsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ListProductsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_products(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_products_flattened_error_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_products(
            product_search_service.ListProductsRequest(), parent="parent_value",
        )


def test_list_products_pager():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_products), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            product_search_service.ListProductsResponse(
                products=[
                    product_search_service.Product(),
                    product_search_service.Product(),
                    product_search_service.Product(),
                ],
                next_page_token="abc",
            ),
            product_search_service.ListProductsResponse(
                products=[], next_page_token="def",
            ),
            product_search_service.ListProductsResponse(
                products=[product_search_service.Product(),], next_page_token="ghi",
            ),
            product_search_service.ListProductsResponse(
                products=[
                    product_search_service.Product(),
                    product_search_service.Product(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_products(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, product_search_service.Product) for i in results)


def test_list_products_pages():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_products), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            product_search_service.ListProductsResponse(
                products=[
                    product_search_service.Product(),
                    product_search_service.Product(),
                    product_search_service.Product(),
                ],
                next_page_token="abc",
            ),
            product_search_service.ListProductsResponse(
                products=[], next_page_token="def",
            ),
            product_search_service.ListProductsResponse(
                products=[product_search_service.Product(),], next_page_token="ghi",
            ),
            product_search_service.ListProductsResponse(
                products=[
                    product_search_service.Product(),
                    product_search_service.Product(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_products(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_products_async_pager():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_products),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            product_search_service.ListProductsResponse(
                products=[
                    product_search_service.Product(),
                    product_search_service.Product(),
                    product_search_service.Product(),
                ],
                next_page_token="abc",
            ),
            product_search_service.ListProductsResponse(
                products=[], next_page_token="def",
            ),
            product_search_service.ListProductsResponse(
                products=[product_search_service.Product(),], next_page_token="ghi",
            ),
            product_search_service.ListProductsResponse(
                products=[
                    product_search_service.Product(),
                    product_search_service.Product(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_products(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, product_search_service.Product) for i in responses)


@pytest.mark.asyncio
async def test_list_products_async_pages():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_products),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            product_search_service.ListProductsResponse(
                products=[
                    product_search_service.Product(),
                    product_search_service.Product(),
                    product_search_service.Product(),
                ],
                next_page_token="abc",
            ),
            product_search_service.ListProductsResponse(
                products=[], next_page_token="def",
            ),
            product_search_service.ListProductsResponse(
                products=[product_search_service.Product(),], next_page_token="ghi",
            ),
            product_search_service.ListProductsResponse(
                products=[
                    product_search_service.Product(),
                    product_search_service.Product(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_products(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_get_product(
    transport: str = "grpc", request_type=product_search_service.GetProductRequest
):
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_product), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.Product(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            product_category="product_category_value",
        )

        response = client.get_product(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == product_search_service.GetProductRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, product_search_service.Product)

    assert response.name == "name_value"

    assert response.display_name == "display_name_value"

    assert response.description == "description_value"

    assert response.product_category == "product_category_value"


def test_get_product_from_dict():
    test_get_product(request_type=dict)


@pytest.mark.asyncio
async def test_get_product_async(transport: str = "grpc_asyncio"):
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = product_search_service.GetProductRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_product), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.Product(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                product_category="product_category_value",
            )
        )

        response = await client.get_product(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, product_search_service.Product)

    assert response.name == "name_value"

    assert response.display_name == "display_name_value"

    assert response.description == "description_value"

    assert response.product_category == "product_category_value"


def test_get_product_field_headers():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.GetProductRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_product), "__call__") as call:
        call.return_value = product_search_service.Product()

        client.get_product(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_product_field_headers_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.GetProductRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_product), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.Product()
        )

        await client.get_product(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_product_flattened():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_product), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.Product()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_product(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_get_product_flattened_error():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_product(
            product_search_service.GetProductRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_product_flattened_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_product), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.Product()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.Product()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_product(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_product_flattened_error_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_product(
            product_search_service.GetProductRequest(), name="name_value",
        )


def test_update_product(
    transport: str = "grpc", request_type=product_search_service.UpdateProductRequest
):
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_product), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.Product(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            product_category="product_category_value",
        )

        response = client.update_product(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == product_search_service.UpdateProductRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, product_search_service.Product)

    assert response.name == "name_value"

    assert response.display_name == "display_name_value"

    assert response.description == "description_value"

    assert response.product_category == "product_category_value"


def test_update_product_from_dict():
    test_update_product(request_type=dict)


@pytest.mark.asyncio
async def test_update_product_async(transport: str = "grpc_asyncio"):
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = product_search_service.UpdateProductRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_product), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.Product(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                product_category="product_category_value",
            )
        )

        response = await client.update_product(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, product_search_service.Product)

    assert response.name == "name_value"

    assert response.display_name == "display_name_value"

    assert response.description == "description_value"

    assert response.product_category == "product_category_value"


def test_update_product_field_headers():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.UpdateProductRequest()
    request.product.name = "product.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_product), "__call__") as call:
        call.return_value = product_search_service.Product()

        client.update_product(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "product.name=product.name/value",) in kw[
        "metadata"
    ]


@pytest.mark.asyncio
async def test_update_product_field_headers_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.UpdateProductRequest()
    request.product.name = "product.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_product), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.Product()
        )

        await client.update_product(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "product.name=product.name/value",) in kw[
        "metadata"
    ]


def test_update_product_flattened():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_product), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.Product()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_product(
            product=product_search_service.Product(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].product == product_search_service.Product(name="name_value")

        assert args[0].update_mask == field_mask.FieldMask(paths=["paths_value"])


def test_update_product_flattened_error():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_product(
            product_search_service.UpdateProductRequest(),
            product=product_search_service.Product(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_product_flattened_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_product), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.Product()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.Product()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_product(
            product=product_search_service.Product(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].product == product_search_service.Product(name="name_value")

        assert args[0].update_mask == field_mask.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_product_flattened_error_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_product(
            product_search_service.UpdateProductRequest(),
            product=product_search_service.Product(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )


def test_delete_product(
    transport: str = "grpc", request_type=product_search_service.DeleteProductRequest
):
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_product), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.delete_product(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == product_search_service.DeleteProductRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_product_from_dict():
    test_delete_product(request_type=dict)


@pytest.mark.asyncio
async def test_delete_product_async(transport: str = "grpc_asyncio"):
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = product_search_service.DeleteProductRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_product), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        response = await client.delete_product(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_product_field_headers():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.DeleteProductRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_product), "__call__") as call:
        call.return_value = None

        client.delete_product(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_product_field_headers_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.DeleteProductRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_product), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        await client.delete_product(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_product_flattened():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_product), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_product(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_delete_product_flattened_error():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_product(
            product_search_service.DeleteProductRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_product_flattened_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_product), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_product(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_product_flattened_error_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_product(
            product_search_service.DeleteProductRequest(), name="name_value",
        )


def test_create_reference_image(
    transport: str = "grpc",
    request_type=product_search_service.CreateReferenceImageRequest,
):
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_reference_image), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ReferenceImage(
            name="name_value", uri="uri_value",
        )

        response = client.create_reference_image(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == product_search_service.CreateReferenceImageRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, product_search_service.ReferenceImage)

    assert response.name == "name_value"

    assert response.uri == "uri_value"


def test_create_reference_image_from_dict():
    test_create_reference_image(request_type=dict)


@pytest.mark.asyncio
async def test_create_reference_image_async(transport: str = "grpc_asyncio"):
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = product_search_service.CreateReferenceImageRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_reference_image), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ReferenceImage(name="name_value", uri="uri_value",)
        )

        response = await client.create_reference_image(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, product_search_service.ReferenceImage)

    assert response.name == "name_value"

    assert response.uri == "uri_value"


def test_create_reference_image_field_headers():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.CreateReferenceImageRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_reference_image), "__call__"
    ) as call:
        call.return_value = product_search_service.ReferenceImage()

        client.create_reference_image(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_reference_image_field_headers_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.CreateReferenceImageRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_reference_image), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ReferenceImage()
        )

        await client.create_reference_image(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_reference_image_flattened():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_reference_image), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ReferenceImage()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_reference_image(
            parent="parent_value",
            reference_image=product_search_service.ReferenceImage(name="name_value"),
            reference_image_id="reference_image_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].reference_image == product_search_service.ReferenceImage(
            name="name_value"
        )

        assert args[0].reference_image_id == "reference_image_id_value"


def test_create_reference_image_flattened_error():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_reference_image(
            product_search_service.CreateReferenceImageRequest(),
            parent="parent_value",
            reference_image=product_search_service.ReferenceImage(name="name_value"),
            reference_image_id="reference_image_id_value",
        )


@pytest.mark.asyncio
async def test_create_reference_image_flattened_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_reference_image), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ReferenceImage()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ReferenceImage()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_reference_image(
            parent="parent_value",
            reference_image=product_search_service.ReferenceImage(name="name_value"),
            reference_image_id="reference_image_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].reference_image == product_search_service.ReferenceImage(
            name="name_value"
        )

        assert args[0].reference_image_id == "reference_image_id_value"


@pytest.mark.asyncio
async def test_create_reference_image_flattened_error_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_reference_image(
            product_search_service.CreateReferenceImageRequest(),
            parent="parent_value",
            reference_image=product_search_service.ReferenceImage(name="name_value"),
            reference_image_id="reference_image_id_value",
        )


def test_delete_reference_image(
    transport: str = "grpc",
    request_type=product_search_service.DeleteReferenceImageRequest,
):
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_reference_image), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.delete_reference_image(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == product_search_service.DeleteReferenceImageRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_reference_image_from_dict():
    test_delete_reference_image(request_type=dict)


@pytest.mark.asyncio
async def test_delete_reference_image_async(transport: str = "grpc_asyncio"):
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = product_search_service.DeleteReferenceImageRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_reference_image), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        response = await client.delete_reference_image(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_reference_image_field_headers():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.DeleteReferenceImageRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_reference_image), "__call__"
    ) as call:
        call.return_value = None

        client.delete_reference_image(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_reference_image_field_headers_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.DeleteReferenceImageRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_reference_image), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        await client.delete_reference_image(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_reference_image_flattened():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_reference_image), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_reference_image(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_delete_reference_image_flattened_error():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_reference_image(
            product_search_service.DeleteReferenceImageRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_reference_image_flattened_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_reference_image), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_reference_image(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_reference_image_flattened_error_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_reference_image(
            product_search_service.DeleteReferenceImageRequest(), name="name_value",
        )


def test_list_reference_images(
    transport: str = "grpc",
    request_type=product_search_service.ListReferenceImagesRequest,
):
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_reference_images), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ListReferenceImagesResponse(
            page_size=951, next_page_token="next_page_token_value",
        )

        response = client.list_reference_images(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == product_search_service.ListReferenceImagesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListReferenceImagesPager)

    assert response.page_size == 951

    assert response.next_page_token == "next_page_token_value"


def test_list_reference_images_from_dict():
    test_list_reference_images(request_type=dict)


@pytest.mark.asyncio
async def test_list_reference_images_async(transport: str = "grpc_asyncio"):
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = product_search_service.ListReferenceImagesRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_reference_images), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ListReferenceImagesResponse(
                page_size=951, next_page_token="next_page_token_value",
            )
        )

        response = await client.list_reference_images(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListReferenceImagesAsyncPager)

    assert response.page_size == 951

    assert response.next_page_token == "next_page_token_value"


def test_list_reference_images_field_headers():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.ListReferenceImagesRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_reference_images), "__call__"
    ) as call:
        call.return_value = product_search_service.ListReferenceImagesResponse()

        client.list_reference_images(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_reference_images_field_headers_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.ListReferenceImagesRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_reference_images), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ListReferenceImagesResponse()
        )

        await client.list_reference_images(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_reference_images_flattened():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_reference_images), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ListReferenceImagesResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_reference_images(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


def test_list_reference_images_flattened_error():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_reference_images(
            product_search_service.ListReferenceImagesRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_reference_images_flattened_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_reference_images), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ListReferenceImagesResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ListReferenceImagesResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_reference_images(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_reference_images_flattened_error_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_reference_images(
            product_search_service.ListReferenceImagesRequest(), parent="parent_value",
        )


def test_list_reference_images_pager():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_reference_images), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            product_search_service.ListReferenceImagesResponse(
                reference_images=[
                    product_search_service.ReferenceImage(),
                    product_search_service.ReferenceImage(),
                    product_search_service.ReferenceImage(),
                ],
                next_page_token="abc",
            ),
            product_search_service.ListReferenceImagesResponse(
                reference_images=[], next_page_token="def",
            ),
            product_search_service.ListReferenceImagesResponse(
                reference_images=[product_search_service.ReferenceImage(),],
                next_page_token="ghi",
            ),
            product_search_service.ListReferenceImagesResponse(
                reference_images=[
                    product_search_service.ReferenceImage(),
                    product_search_service.ReferenceImage(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_reference_images(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(
            isinstance(i, product_search_service.ReferenceImage) for i in results
        )


def test_list_reference_images_pages():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_reference_images), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            product_search_service.ListReferenceImagesResponse(
                reference_images=[
                    product_search_service.ReferenceImage(),
                    product_search_service.ReferenceImage(),
                    product_search_service.ReferenceImage(),
                ],
                next_page_token="abc",
            ),
            product_search_service.ListReferenceImagesResponse(
                reference_images=[], next_page_token="def",
            ),
            product_search_service.ListReferenceImagesResponse(
                reference_images=[product_search_service.ReferenceImage(),],
                next_page_token="ghi",
            ),
            product_search_service.ListReferenceImagesResponse(
                reference_images=[
                    product_search_service.ReferenceImage(),
                    product_search_service.ReferenceImage(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_reference_images(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_reference_images_async_pager():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_reference_images),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            product_search_service.ListReferenceImagesResponse(
                reference_images=[
                    product_search_service.ReferenceImage(),
                    product_search_service.ReferenceImage(),
                    product_search_service.ReferenceImage(),
                ],
                next_page_token="abc",
            ),
            product_search_service.ListReferenceImagesResponse(
                reference_images=[], next_page_token="def",
            ),
            product_search_service.ListReferenceImagesResponse(
                reference_images=[product_search_service.ReferenceImage(),],
                next_page_token="ghi",
            ),
            product_search_service.ListReferenceImagesResponse(
                reference_images=[
                    product_search_service.ReferenceImage(),
                    product_search_service.ReferenceImage(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_reference_images(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(
            isinstance(i, product_search_service.ReferenceImage) for i in responses
        )


@pytest.mark.asyncio
async def test_list_reference_images_async_pages():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_reference_images),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            product_search_service.ListReferenceImagesResponse(
                reference_images=[
                    product_search_service.ReferenceImage(),
                    product_search_service.ReferenceImage(),
                    product_search_service.ReferenceImage(),
                ],
                next_page_token="abc",
            ),
            product_search_service.ListReferenceImagesResponse(
                reference_images=[], next_page_token="def",
            ),
            product_search_service.ListReferenceImagesResponse(
                reference_images=[product_search_service.ReferenceImage(),],
                next_page_token="ghi",
            ),
            product_search_service.ListReferenceImagesResponse(
                reference_images=[
                    product_search_service.ReferenceImage(),
                    product_search_service.ReferenceImage(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_reference_images(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_get_reference_image(
    transport: str = "grpc",
    request_type=product_search_service.GetReferenceImageRequest,
):
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_reference_image), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ReferenceImage(
            name="name_value", uri="uri_value",
        )

        response = client.get_reference_image(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == product_search_service.GetReferenceImageRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, product_search_service.ReferenceImage)

    assert response.name == "name_value"

    assert response.uri == "uri_value"


def test_get_reference_image_from_dict():
    test_get_reference_image(request_type=dict)


@pytest.mark.asyncio
async def test_get_reference_image_async(transport: str = "grpc_asyncio"):
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = product_search_service.GetReferenceImageRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_reference_image), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ReferenceImage(name="name_value", uri="uri_value",)
        )

        response = await client.get_reference_image(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, product_search_service.ReferenceImage)

    assert response.name == "name_value"

    assert response.uri == "uri_value"


def test_get_reference_image_field_headers():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.GetReferenceImageRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_reference_image), "__call__"
    ) as call:
        call.return_value = product_search_service.ReferenceImage()

        client.get_reference_image(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_reference_image_field_headers_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.GetReferenceImageRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_reference_image), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ReferenceImage()
        )

        await client.get_reference_image(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_reference_image_flattened():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_reference_image), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ReferenceImage()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_reference_image(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_get_reference_image_flattened_error():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_reference_image(
            product_search_service.GetReferenceImageRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_reference_image_flattened_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_reference_image), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ReferenceImage()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ReferenceImage()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_reference_image(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_reference_image_flattened_error_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_reference_image(
            product_search_service.GetReferenceImageRequest(), name="name_value",
        )


def test_add_product_to_product_set(
    transport: str = "grpc",
    request_type=product_search_service.AddProductToProductSetRequest,
):
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.add_product_to_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.add_product_to_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == product_search_service.AddProductToProductSetRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_add_product_to_product_set_from_dict():
    test_add_product_to_product_set(request_type=dict)


@pytest.mark.asyncio
async def test_add_product_to_product_set_async(transport: str = "grpc_asyncio"):
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = product_search_service.AddProductToProductSetRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.add_product_to_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        response = await client.add_product_to_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_add_product_to_product_set_field_headers():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.AddProductToProductSetRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.add_product_to_product_set), "__call__"
    ) as call:
        call.return_value = None

        client.add_product_to_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_add_product_to_product_set_field_headers_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.AddProductToProductSetRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.add_product_to_product_set), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        await client.add_product_to_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_add_product_to_product_set_flattened():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.add_product_to_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.add_product_to_product_set(
            name="name_value", product="product_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].product == "product_value"


def test_add_product_to_product_set_flattened_error():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.add_product_to_product_set(
            product_search_service.AddProductToProductSetRequest(),
            name="name_value",
            product="product_value",
        )


@pytest.mark.asyncio
async def test_add_product_to_product_set_flattened_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.add_product_to_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.add_product_to_product_set(
            name="name_value", product="product_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].product == "product_value"


@pytest.mark.asyncio
async def test_add_product_to_product_set_flattened_error_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.add_product_to_product_set(
            product_search_service.AddProductToProductSetRequest(),
            name="name_value",
            product="product_value",
        )


def test_remove_product_from_product_set(
    transport: str = "grpc",
    request_type=product_search_service.RemoveProductFromProductSetRequest,
):
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.remove_product_from_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.remove_product_from_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == product_search_service.RemoveProductFromProductSetRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_remove_product_from_product_set_from_dict():
    test_remove_product_from_product_set(request_type=dict)


@pytest.mark.asyncio
async def test_remove_product_from_product_set_async(transport: str = "grpc_asyncio"):
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = product_search_service.RemoveProductFromProductSetRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.remove_product_from_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        response = await client.remove_product_from_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_remove_product_from_product_set_field_headers():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.RemoveProductFromProductSetRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.remove_product_from_product_set), "__call__"
    ) as call:
        call.return_value = None

        client.remove_product_from_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_remove_product_from_product_set_field_headers_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.RemoveProductFromProductSetRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.remove_product_from_product_set), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        await client.remove_product_from_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_remove_product_from_product_set_flattened():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.remove_product_from_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.remove_product_from_product_set(
            name="name_value", product="product_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].product == "product_value"


def test_remove_product_from_product_set_flattened_error():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.remove_product_from_product_set(
            product_search_service.RemoveProductFromProductSetRequest(),
            name="name_value",
            product="product_value",
        )


@pytest.mark.asyncio
async def test_remove_product_from_product_set_flattened_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.remove_product_from_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.remove_product_from_product_set(
            name="name_value", product="product_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].product == "product_value"


@pytest.mark.asyncio
async def test_remove_product_from_product_set_flattened_error_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.remove_product_from_product_set(
            product_search_service.RemoveProductFromProductSetRequest(),
            name="name_value",
            product="product_value",
        )


def test_list_products_in_product_set(
    transport: str = "grpc",
    request_type=product_search_service.ListProductsInProductSetRequest,
):
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_products_in_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ListProductsInProductSetResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_products_in_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == product_search_service.ListProductsInProductSetRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListProductsInProductSetPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_products_in_product_set_from_dict():
    test_list_products_in_product_set(request_type=dict)


@pytest.mark.asyncio
async def test_list_products_in_product_set_async(transport: str = "grpc_asyncio"):
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = product_search_service.ListProductsInProductSetRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_products_in_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ListProductsInProductSetResponse(
                next_page_token="next_page_token_value",
            )
        )

        response = await client.list_products_in_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListProductsInProductSetAsyncPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_products_in_product_set_field_headers():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.ListProductsInProductSetRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_products_in_product_set), "__call__"
    ) as call:
        call.return_value = product_search_service.ListProductsInProductSetResponse()

        client.list_products_in_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_products_in_product_set_field_headers_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.ListProductsInProductSetRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_products_in_product_set), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ListProductsInProductSetResponse()
        )

        await client.list_products_in_product_set(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_list_products_in_product_set_flattened():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_products_in_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ListProductsInProductSetResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_products_in_product_set(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_list_products_in_product_set_flattened_error():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_products_in_product_set(
            product_search_service.ListProductsInProductSetRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_list_products_in_product_set_flattened_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_products_in_product_set), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = product_search_service.ListProductsInProductSetResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            product_search_service.ListProductsInProductSetResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_products_in_product_set(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_list_products_in_product_set_flattened_error_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_products_in_product_set(
            product_search_service.ListProductsInProductSetRequest(), name="name_value",
        )


def test_list_products_in_product_set_pager():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_products_in_product_set), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            product_search_service.ListProductsInProductSetResponse(
                products=[
                    product_search_service.Product(),
                    product_search_service.Product(),
                    product_search_service.Product(),
                ],
                next_page_token="abc",
            ),
            product_search_service.ListProductsInProductSetResponse(
                products=[], next_page_token="def",
            ),
            product_search_service.ListProductsInProductSetResponse(
                products=[product_search_service.Product(),], next_page_token="ghi",
            ),
            product_search_service.ListProductsInProductSetResponse(
                products=[
                    product_search_service.Product(),
                    product_search_service.Product(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("name", ""),)),
        )
        pager = client.list_products_in_product_set(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, product_search_service.Product) for i in results)


def test_list_products_in_product_set_pages():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_products_in_product_set), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            product_search_service.ListProductsInProductSetResponse(
                products=[
                    product_search_service.Product(),
                    product_search_service.Product(),
                    product_search_service.Product(),
                ],
                next_page_token="abc",
            ),
            product_search_service.ListProductsInProductSetResponse(
                products=[], next_page_token="def",
            ),
            product_search_service.ListProductsInProductSetResponse(
                products=[product_search_service.Product(),], next_page_token="ghi",
            ),
            product_search_service.ListProductsInProductSetResponse(
                products=[
                    product_search_service.Product(),
                    product_search_service.Product(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_products_in_product_set(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_products_in_product_set_async_pager():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_products_in_product_set),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            product_search_service.ListProductsInProductSetResponse(
                products=[
                    product_search_service.Product(),
                    product_search_service.Product(),
                    product_search_service.Product(),
                ],
                next_page_token="abc",
            ),
            product_search_service.ListProductsInProductSetResponse(
                products=[], next_page_token="def",
            ),
            product_search_service.ListProductsInProductSetResponse(
                products=[product_search_service.Product(),], next_page_token="ghi",
            ),
            product_search_service.ListProductsInProductSetResponse(
                products=[
                    product_search_service.Product(),
                    product_search_service.Product(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_products_in_product_set(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, product_search_service.Product) for i in responses)


@pytest.mark.asyncio
async def test_list_products_in_product_set_async_pages():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_products_in_product_set),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            product_search_service.ListProductsInProductSetResponse(
                products=[
                    product_search_service.Product(),
                    product_search_service.Product(),
                    product_search_service.Product(),
                ],
                next_page_token="abc",
            ),
            product_search_service.ListProductsInProductSetResponse(
                products=[], next_page_token="def",
            ),
            product_search_service.ListProductsInProductSetResponse(
                products=[product_search_service.Product(),], next_page_token="ghi",
            ),
            product_search_service.ListProductsInProductSetResponse(
                products=[
                    product_search_service.Product(),
                    product_search_service.Product(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (
            await client.list_products_in_product_set(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_import_product_sets(
    transport: str = "grpc",
    request_type=product_search_service.ImportProductSetsRequest,
):
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.import_product_sets), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.import_product_sets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == product_search_service.ImportProductSetsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_import_product_sets_from_dict():
    test_import_product_sets(request_type=dict)


@pytest.mark.asyncio
async def test_import_product_sets_async(transport: str = "grpc_asyncio"):
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = product_search_service.ImportProductSetsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.import_product_sets), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )

        response = await client.import_product_sets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_import_product_sets_field_headers():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.ImportProductSetsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.import_product_sets), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")

        client.import_product_sets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_import_product_sets_field_headers_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.ImportProductSetsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.import_product_sets), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )

        await client.import_product_sets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_import_product_sets_flattened():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.import_product_sets), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.import_product_sets(
            parent="parent_value",
            input_config=product_search_service.ImportProductSetsInputConfig(
                gcs_source=product_search_service.ImportProductSetsGcsSource(
                    csv_file_uri="csv_file_uri_value"
                )
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[
            0
        ].input_config == product_search_service.ImportProductSetsInputConfig(
            gcs_source=product_search_service.ImportProductSetsGcsSource(
                csv_file_uri="csv_file_uri_value"
            )
        )


def test_import_product_sets_flattened_error():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.import_product_sets(
            product_search_service.ImportProductSetsRequest(),
            parent="parent_value",
            input_config=product_search_service.ImportProductSetsInputConfig(
                gcs_source=product_search_service.ImportProductSetsGcsSource(
                    csv_file_uri="csv_file_uri_value"
                )
            ),
        )


@pytest.mark.asyncio
async def test_import_product_sets_flattened_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.import_product_sets), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.import_product_sets(
            parent="parent_value",
            input_config=product_search_service.ImportProductSetsInputConfig(
                gcs_source=product_search_service.ImportProductSetsGcsSource(
                    csv_file_uri="csv_file_uri_value"
                )
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[
            0
        ].input_config == product_search_service.ImportProductSetsInputConfig(
            gcs_source=product_search_service.ImportProductSetsGcsSource(
                csv_file_uri="csv_file_uri_value"
            )
        )


@pytest.mark.asyncio
async def test_import_product_sets_flattened_error_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.import_product_sets(
            product_search_service.ImportProductSetsRequest(),
            parent="parent_value",
            input_config=product_search_service.ImportProductSetsInputConfig(
                gcs_source=product_search_service.ImportProductSetsGcsSource(
                    csv_file_uri="csv_file_uri_value"
                )
            ),
        )


def test_purge_products(
    transport: str = "grpc", request_type=product_search_service.PurgeProductsRequest
):
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.purge_products), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.purge_products(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == product_search_service.PurgeProductsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_purge_products_from_dict():
    test_purge_products(request_type=dict)


@pytest.mark.asyncio
async def test_purge_products_async(transport: str = "grpc_asyncio"):
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = product_search_service.PurgeProductsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.purge_products), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )

        response = await client.purge_products(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_purge_products_field_headers():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.PurgeProductsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.purge_products), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")

        client.purge_products(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_purge_products_field_headers_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = product_search_service.PurgeProductsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.purge_products), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )

        await client.purge_products(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_purge_products_flattened():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.purge_products), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.purge_products(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


def test_purge_products_flattened_error():
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.purge_products(
            product_search_service.PurgeProductsRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_purge_products_flattened_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.purge_products), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.purge_products(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_purge_products_flattened_error_async():
    client = ProductSearchAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.purge_products(
            product_search_service.PurgeProductsRequest(), parent="parent_value",
        )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.ProductSearchGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = ProductSearchClient(
            credentials=credentials.AnonymousCredentials(), transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.ProductSearchGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = ProductSearchClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.ProductSearchGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = ProductSearchClient(
            client_options={"scopes": ["1", "2"]}, transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.ProductSearchGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = ProductSearchClient(transport=transport)
    assert client._transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.ProductSearchGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.ProductSearchGrpcAsyncIOTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = ProductSearchClient(credentials=credentials.AnonymousCredentials(),)
    assert isinstance(client._transport, transports.ProductSearchGrpcTransport,)


def test_product_search_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(exceptions.DuplicateCredentialArgs):
        transport = transports.ProductSearchTransport(
            credentials=credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_product_search_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.vision_v1.services.product_search.transports.ProductSearchTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.ProductSearchTransport(
            credentials=credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "create_product_set",
        "list_product_sets",
        "get_product_set",
        "update_product_set",
        "delete_product_set",
        "create_product",
        "list_products",
        "get_product",
        "update_product",
        "delete_product",
        "create_reference_image",
        "delete_reference_image",
        "list_reference_images",
        "get_reference_image",
        "add_product_to_product_set",
        "remove_product_from_product_set",
        "list_products_in_product_set",
        "import_product_sets",
        "purge_products",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client


def test_product_search_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        auth, "load_credentials_from_file"
    ) as load_creds, mock.patch(
        "google.cloud.vision_v1.services.product_search.transports.ProductSearchTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.ProductSearchTransport(
            credentials_file="credentials.json", quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/cloud-vision",
            ),
            quota_project_id="octopus",
        )


def test_product_search_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        ProductSearchClient()
        adc.assert_called_once_with(
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/cloud-vision",
            ),
            quota_project_id=None,
        )


def test_product_search_transport_auth_adc():
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transports.ProductSearchGrpcTransport(
            host="squid.clam.whelk", quota_project_id="octopus"
        )
        adc.assert_called_once_with(
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/cloud-vision",
            ),
            quota_project_id="octopus",
        )


def test_product_search_host_no_port():
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="vision.googleapis.com"
        ),
    )
    assert client._transport._host == "vision.googleapis.com:443"


def test_product_search_host_with_port():
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="vision.googleapis.com:8000"
        ),
    )
    assert client._transport._host == "vision.googleapis.com:8000"


def test_product_search_grpc_transport_channel():
    channel = grpc.insecure_channel("http://localhost/")

    # Check that if channel is provided, mtls endpoint and client_cert_source
    # won't be used.
    callback = mock.MagicMock()
    transport = transports.ProductSearchGrpcTransport(
        host="squid.clam.whelk",
        channel=channel,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=callback,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert not callback.called


def test_product_search_grpc_asyncio_transport_channel():
    channel = aio.insecure_channel("http://localhost/")

    # Check that if channel is provided, mtls endpoint and client_cert_source
    # won't be used.
    callback = mock.MagicMock()
    transport = transports.ProductSearchGrpcAsyncIOTransport(
        host="squid.clam.whelk",
        channel=channel,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=callback,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert not callback.called


@mock.patch("grpc.ssl_channel_credentials", autospec=True)
@mock.patch("google.api_core.grpc_helpers.create_channel", autospec=True)
def test_product_search_grpc_transport_channel_mtls_with_client_cert_source(
    grpc_create_channel, grpc_ssl_channel_cred
):
    # Check that if channel is None, but api_mtls_endpoint and client_cert_source
    # are provided, then a mTLS channel will be created.
    mock_cred = mock.Mock()

    mock_ssl_cred = mock.Mock()
    grpc_ssl_channel_cred.return_value = mock_ssl_cred

    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    transport = transports.ProductSearchGrpcTransport(
        host="squid.clam.whelk",
        credentials=mock_cred,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=client_cert_source_callback,
    )
    grpc_ssl_channel_cred.assert_called_once_with(
        certificate_chain=b"cert bytes", private_key=b"key bytes"
    )
    grpc_create_channel.assert_called_once_with(
        "mtls.squid.clam.whelk:443",
        credentials=mock_cred,
        credentials_file=None,
        scopes=(
            "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/cloud-vision",
        ),
        ssl_credentials=mock_ssl_cred,
        quota_project_id=None,
    )
    assert transport.grpc_channel == mock_grpc_channel


@mock.patch("grpc.ssl_channel_credentials", autospec=True)
@mock.patch("google.api_core.grpc_helpers_async.create_channel", autospec=True)
def test_product_search_grpc_asyncio_transport_channel_mtls_with_client_cert_source(
    grpc_create_channel, grpc_ssl_channel_cred
):
    # Check that if channel is None, but api_mtls_endpoint and client_cert_source
    # are provided, then a mTLS channel will be created.
    mock_cred = mock.Mock()

    mock_ssl_cred = mock.Mock()
    grpc_ssl_channel_cred.return_value = mock_ssl_cred

    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    transport = transports.ProductSearchGrpcAsyncIOTransport(
        host="squid.clam.whelk",
        credentials=mock_cred,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=client_cert_source_callback,
    )
    grpc_ssl_channel_cred.assert_called_once_with(
        certificate_chain=b"cert bytes", private_key=b"key bytes"
    )
    grpc_create_channel.assert_called_once_with(
        "mtls.squid.clam.whelk:443",
        credentials=mock_cred,
        credentials_file=None,
        scopes=(
            "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/cloud-vision",
        ),
        ssl_credentials=mock_ssl_cred,
        quota_project_id=None,
    )
    assert transport.grpc_channel == mock_grpc_channel


@pytest.mark.parametrize(
    "api_mtls_endpoint", ["mtls.squid.clam.whelk", "mtls.squid.clam.whelk:443"]
)
@mock.patch("google.api_core.grpc_helpers.create_channel", autospec=True)
def test_product_search_grpc_transport_channel_mtls_with_adc(
    grpc_create_channel, api_mtls_endpoint
):
    # Check that if channel and client_cert_source are None, but api_mtls_endpoint
    # is provided, then a mTLS channel will be created with SSL ADC.
    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    # Mock google.auth.transport.grpc.SslCredentials class.
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        mock_cred = mock.Mock()
        transport = transports.ProductSearchGrpcTransport(
            host="squid.clam.whelk",
            credentials=mock_cred,
            api_mtls_endpoint=api_mtls_endpoint,
            client_cert_source=None,
        )
        grpc_create_channel.assert_called_once_with(
            "mtls.squid.clam.whelk:443",
            credentials=mock_cred,
            credentials_file=None,
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/cloud-vision",
            ),
            ssl_credentials=mock_ssl_cred,
            quota_project_id=None,
        )
        assert transport.grpc_channel == mock_grpc_channel


@pytest.mark.parametrize(
    "api_mtls_endpoint", ["mtls.squid.clam.whelk", "mtls.squid.clam.whelk:443"]
)
@mock.patch("google.api_core.grpc_helpers_async.create_channel", autospec=True)
def test_product_search_grpc_asyncio_transport_channel_mtls_with_adc(
    grpc_create_channel, api_mtls_endpoint
):
    # Check that if channel and client_cert_source are None, but api_mtls_endpoint
    # is provided, then a mTLS channel will be created with SSL ADC.
    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    # Mock google.auth.transport.grpc.SslCredentials class.
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        mock_cred = mock.Mock()
        transport = transports.ProductSearchGrpcAsyncIOTransport(
            host="squid.clam.whelk",
            credentials=mock_cred,
            api_mtls_endpoint=api_mtls_endpoint,
            client_cert_source=None,
        )
        grpc_create_channel.assert_called_once_with(
            "mtls.squid.clam.whelk:443",
            credentials=mock_cred,
            credentials_file=None,
            scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/cloud-vision",
            ),
            ssl_credentials=mock_ssl_cred,
            quota_project_id=None,
        )
        assert transport.grpc_channel == mock_grpc_channel


def test_product_search_grpc_lro_client():
    client = ProductSearchClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc",
    )
    transport = client._transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_product_search_grpc_lro_async_client():
    client = ProductSearchAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc_asyncio",
    )
    transport = client._client._transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsAsyncClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_reference_image_path():
    project = "squid"
    location = "clam"
    product = "whelk"
    reference_image = "octopus"

    expected = "projects/{project}/locations/{location}/products/{product}/referenceImages/{reference_image}".format(
        project=project,
        location=location,
        product=product,
        reference_image=reference_image,
    )
    actual = ProductSearchClient.reference_image_path(
        project, location, product, reference_image
    )
    assert expected == actual


def test_parse_reference_image_path():
    expected = {
        "project": "oyster",
        "location": "nudibranch",
        "product": "cuttlefish",
        "reference_image": "mussel",
    }
    path = ProductSearchClient.reference_image_path(**expected)

    # Check that the path construction is reversible.
    actual = ProductSearchClient.parse_reference_image_path(path)
    assert expected == actual


def test_product_path():
    project = "squid"
    location = "clam"
    product = "whelk"

    expected = "projects/{project}/locations/{location}/products/{product}".format(
        project=project, location=location, product=product,
    )
    actual = ProductSearchClient.product_path(project, location, product)
    assert expected == actual


def test_parse_product_path():
    expected = {
        "project": "octopus",
        "location": "oyster",
        "product": "nudibranch",
    }
    path = ProductSearchClient.product_path(**expected)

    # Check that the path construction is reversible.
    actual = ProductSearchClient.parse_product_path(path)
    assert expected == actual


def test_product_set_path():
    project = "squid"
    location = "clam"
    product_set = "whelk"

    expected = "projects/{project}/locations/{location}/productSets/{product_set}".format(
        project=project, location=location, product_set=product_set,
    )
    actual = ProductSearchClient.product_set_path(project, location, product_set)
    assert expected == actual


def test_parse_product_set_path():
    expected = {
        "project": "octopus",
        "location": "oyster",
        "product_set": "nudibranch",
    }
    path = ProductSearchClient.product_set_path(**expected)

    # Check that the path construction is reversible.
    actual = ProductSearchClient.parse_product_set_path(path)
    assert expected == actual


def test_client_withDEFAULT_CLIENT_INFO():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.ProductSearchTransport, "_prep_wrapped_messages"
    ) as prep:
        client = ProductSearchClient(
            credentials=credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.ProductSearchTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = ProductSearchClient.get_transport_class()
        transport = transport_class(
            credentials=credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)
