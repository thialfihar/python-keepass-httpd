# -*- coding: utf-8 -*-
import mock
import pytest

from keepass_http.httpd import requests


class TestBackend(mock.Mock):
    get_config = mock.Mock()


class TestConf(mock.Mock):
    backend = TestBackend()


class TestAES(mock.Mock):
    pass

class TestKPC(mock.Mock):
    decrypt = mock.Mock(return_value=None)
    encrypt = mock.Mock()


class ImplementedRequest(requests.Request):

    def process(self, request_dict):
        return


def test_baserequest_is_abstract():
    with pytest.raises(TypeError):
        requests.Request(None)

@mock.patch("keepass_http.httpd.requests.Conf", TestConf)
def test_baserequest_authenticate_broken_request_dict():
    request = ImplementedRequest()

    with pytest.raises(KeyError):
        request._request_dict = {}
        request.authenticate()

@mock.patch("keepass_http.httpd.requests.Conf", TestConf)
@mock.patch.object(TestBackend, "get_config")
def test_baserequest_authenticate_unknown_key(mock_get_config):
    request = ImplementedRequest()

    mock_get_config.return_value = None
    with pytest.raises(requests.AuthenticationError):
        request._request_dict = {"Id": "some client name",
                                 "Key": "some unknown key"}
        request.authenticate()

@mock.patch("keepass_http.httpd.requests.Conf", TestConf)
@mock.patch.object(TestBackend, "get_config")
def test_baserequest_authenticate_broken_request_dict_2(mock_get_config):
    request = ImplementedRequest()

    mock_get_config.return_value = "known key"

    with pytest.raises(KeyError):
        request._request_dict = {"Id": "some client name",
                                 "Key": "some known key"}
        request.authenticate()

    with pytest.raises(KeyError):
        request._request_dict = {"Id": "some client name",
                                 "Nonce": "some nonce"}
        request.authenticate()

@mock.patch("keepass_http.httpd.requests.Conf", TestConf)
@mock.patch("keepass_http.httpd.requests.AESCipher")
@mock.patch.object(TestBackend, "get_config")
def test_baserequest_authenticate_with_kpc_invalid(mock_get_config, mock_kpc):
    mock_get_config.return_value = "known key"

    aes = TestAES()
    mock_kpc.return_value = aes

    aes.is_valid = mock.Mock(return_value=False)

    request_dict = {"Id": "some client name",
                    "Key": "some known key",
                    "Nonce": "some nonce",
                    "Verifier": "some verifier"}

    request = ImplementedRequest()
    with pytest.raises(requests.InvalidAuthentication):
        request._request_dict = request_dict
        request.authenticate()


@mock.patch("keepass_http.httpd.requests.Conf", TestConf)
@mock.patch("keepass_http.httpd.requests.AESCipher")
@mock.patch.object(TestBackend, "get_config")
def test_baserequest_authenticate_with_kpc_valid(mock_get_config, mock_kpc):
    mock_get_config.return_value = "known key"

    aes = TestAES()
    mock_kpc.return_value = aes

    aes.is_valid = mock.Mock(return_value=True)

    request_dict = {"Id": "some client name",
                    "Key": "some known key",
                    "Nonce": "some nonce",
                    "Verifier": "some verifier"}

    request = ImplementedRequest()
    request._request_dict = request_dict
    request.authenticate()

@mock.patch("keepass_http.httpd.requests.Conf", TestConf)
@mock.patch("keepass_http.httpd.requests.AESCipher")
@mock.patch.object(TestBackend, "get_config")
def test_baserequest_authenticate_with_kpc_get_kpc_authenticated(mock_get_config, mock_kpc):
    mock_get_config.return_value = "known key"

    aes = TestAES()
    mock_kpc.return_value = aes

    aes.is_valid = mock.Mock(return_value=True)
    aes._kpc = mock.Mock(return_value=aes)

    request_dict = {"Id": "some client name",
                    "Key": "some known key",
                    "Nonce": "some nonce",
                    "Verifier": "some verifier"}

    request = ImplementedRequest()
    request._request_dict = request_dict
    request.authenticate()
    request.get_kpc()


@mock.patch.object(TestBackend, "get_config")
def test_baserequest_authenticate_with_kpc_get_kpc_not_authenticated(mock_get_config):
    mock_get_config.return_value = "known key"

    aes = TestAES()
    aes._kpc = mock.Mock(return_value=None)

    request = ImplementedRequest()
    with pytest.raises(requests.NotAuthenticated):
        request.get_kpc()

@mock.patch("keepass_http.httpd.requests.Conf", TestConf)
@mock.patch("keepass_http.httpd.requests.AESCipher")
@mock.patch.object(TestBackend, "get_config")
def test_baserequest_set_verifier_with_valid_key(mock_get_config, mock_kpc):
    mock_get_config.return_value = "known key"

    aes = TestAES()
    mock_kpc.return_value = aes

    request = ImplementedRequest()

    request.set_verifier("some client")

    assert request.response_dict['Nonce'] != None
    assert request.response_dict['Verifier'] != None

@mock.patch("keepass_http.httpd.requests.Conf", TestConf)
@mock.patch.object(TestBackend, "get_config")
def test_baserequest_set_verifier_with_invalid_key(mock_get_config):
    mock_get_config.return_value = None

    aes = TestAES()
    aes._kpc = mock.Mock(return_value=None)

    request = ImplementedRequest()
    with pytest.raises(requests.AuthenticationError):
	       request.set_verifier("nomatterwhat")
