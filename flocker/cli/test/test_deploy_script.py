# Copyright Hybrid Logic Ltd.  See LICENSE file for details.

"""
Unit tests for the implementation ``flocker-deploy``.
"""
from twisted.python.filepath import FilePath
from twisted.python.usage import UsageError
from twisted.trial.unittest import TestCase, SynchronousTestCase

from ...testtools import FlockerScriptTestsMixin, StandardOptionsTestsMixin
from ..script import DeployScript, DeployOptions
from ...node import Application, Deployment, DockerImage, Node

class FlockerDeployTests(FlockerScriptTestsMixin, TestCase):
    """Tests for ``flocker-deploy``."""
    script = DeployScript
    options = DeployOptions
    command_name = u'flocker-deploy'


class DeployOptionsTests(StandardOptionsTestsMixin, SynchronousTestCase):
    """Tests for :class:`DeployOptions`."""
    options = DeployOptions

    def test_deploy_must_exist(self):
        """
        A ``UsageError`` is raised if the ``deployment_config`` file does not
        exist.
        """
        options = self.options()
        app = self.mktemp()
        FilePath(app).touch()
        deploy = b"/path/to/non-existent-file.cfg"
        exception = self.assertRaises(UsageError, options.parseOptions,
                                      [deploy, app])
        self.assertEqual('No file exists at {deploy}'.format(deploy=deploy),
                         str(exception))

    def test_app_must_exist(self):
        """
        A ``UsageError`` is raised if the ``app_config`` file does not
        exist.
        """
        options = self.options()
        deploy = self.mktemp()
        FilePath(deploy).touch()
        app = b"/path/to/non-existent-file.cfg"
        exception = self.assertRaises(UsageError, options.parseOptions,
                                      [deploy, app])
        self.assertEqual('No file exists at {app}'.format(app=app),
                         str(exception))

    def test_deployment_object(self):
        """
        A ``Deployment`` object is assigned to the ``Options`` instance.
        """
        options = self.options()
        deployment_configuration_path = self.mktemp()
        deployment_configuration = FilePath(deployment_configuration_path)
        deployment_configuration.setContent("""
        {"version": 1,
         "nodes": {
             "node1": ["mysql-hybridcluster"],
             "node2": ["site-hybridcluster.com"]
         }
        }
        """)

        application_configuration_path = self.mktemp()
        application_configuration = FilePath(application_configuration_path)
        application_configuration.setContent("""
        {"version": 1,
         "applications": {
             "mysql-hybridcluster": {"image": "hybridlogic/mysql5.9:latest"},
             "site-hybridcluster.com": {"image": "hybridlogic/nginx:v1.2.3"}
         }
        }
        """)

        options.parseOptions([application_configuration_path, deployment_configuration_path])
        expected = Deployment(nodes=frozenset([
            Node(
                hostname=u'node1',
                applications=frozenset([
                    Application(
                        name=u'mysql-hybridcluster',
                        image=DockerImage(
                            repository=u'hybridlogic/mysql5.9',
                            tag=u'latest'
                        )
                    )
                ]),
            ),
            Node(
                hostname=u'node2',
                applications=frozenset([
                    Application(
                        name=u'site-hybridcluster.com',
                        image=DockerImage(
                            repository=u'hybridlogic/nginx',
                            tag=u'v1.2.3'
                        )
                    )
                ]),
            )
        ]))

        self.assertEqual(expected, options['deployment'])


class FlockerDeployMainTests(SynchronousTestCase):
    """
    Tests for ``DeployScript.main``.
    """
    def test_deferred_result(self):
        """
        ``DeployScript.main`` returns a ``Deferred`` on success.
        """
        script = DeployScript()
        dummy_reactor = object()
        options = {}
        self.assertIs(
            None,
            self.successResultOf(script.main(dummy_reactor, options))
        )
