import json
from haas.client.base import ClientBase
from haas.client import errors


class Node(ClientBase):
    """ Consists of calls to query and manipulate node related
    objects and relations.
    """

    def list(self, is_free):
        """ List all nodes that HIL manages """
        self.is_free = is_free
        url = self.object_url('nodes', self.is_free)
        q = self.s.get(url)
        if q.ok:
            return q.json()
        elif q.status_code == 401:
            raise errors.AuthenticationError(
                  "Make sure credentials match chosen authentication backend."
                  )

    def show(self, node_name):
        """ Shows attributes of a given node """

        self.node_name = node_name
        url = self.object_url('node', self.node_name)
        q = self.s.get(url)
        return q.json()

    def register(self, node, subtype, *args):
        """ Register a node with appropriate OBM driver. """
#       Registering a node requires apriori knowledge of the
#       available OBM driver and its corresponding arguments.
#       We assume that the HIL administrator is aware as to which
#       Node requires which OBM, and knows arguments required
#       for successful node registration.

        self.node = node
        self.subtype = subtype
        obm_api = "http://schema.massopencloud.org/haas/v0/obm/"
        obm_types = ["ipmi", "mock"]
#       FIXME: In future obm_types should be dynamically fetched
#        from haas.cfg, need a new api call for querying available
#        and currently active drivers for HIL
        pass

    def delete(self, node_name):
        """ Deletes the node from database. """
        self.node_name = node_name
        url = self.object_url('node', self.node_name)
        q = self.s.delete(url)
        if q.ok:
            return
        elif q.status_code == 409:
            raise errors.BlockedError(
                    "Make sure all nics are removed before deleting the node"
                    )
        elif q.status_code == 404:
            raise errors.NotFoundError(
                    "No such node exist. Nothing to delete."
                    )

    def power_cycle(self, node_name):
        """ Power cycles the <node> """
        self.node_name = node_name
        url = self.object_url('node', node_name, 'power_cycle')
        q = self.s.post(url)
        if q.ok:
            return
        elif q.status_code == 409:
            raise errors.BlockedError(
                    "Operation blocked by other pending operations"
                    )
        elif q.status_code == 500:
            raise errors.NotFoundError(
                    "Operation Failed. This is a server-side problem. "
                    "Contact your HIL Administrator. "
                    )

    def power_off(self, node_name):
        """ Power offs the <node> """
        self.node_name = node_name
        url = self.object_url('node', self.node_name, 'power_off')
        q = self.s.post(url)
        if q.ok:
            return
        elif q.status_code == 404:
            raise errors.NotFoundError("Node not found.")
        elif q.status_code == 409:
            raise errors.BlockedError(
                    "Operation blocked by other pending operations"
                    )
        elif q.status_code == 500:
            raise errors.NotFoundError(
                    "Operation Failed. Contact your system administrator"
                    )

    def add_nic(self, node_name, nic_name, macaddr):
        """ adds a <nic> to <node>"""
        self.node_name = node_name
        self.nic_name = nic_name
        self.macaddr = macaddr
        url = self.object_url('node', self.node_name, 'nic', self.nic_name)
        payload = json.dumps({'macaddr': self.macaddr})
        q = self.s.put(url, data=payload)
        if q.ok:
            return
        elif q.status_code == 404:
            raise errors.NotFoundError(
                    "Nic cannot be added. Node does not exist."
                    )
        elif q.status_code == 409:
            raise errors.DuplicateError(
                    "Nic already exists."
                    )

    def remove_nic(self, node_name, nic_name):
        """ remove a <nic> from <node>"""
        self.node_name = node_name
        self.nic_name = nic_name
        url = self.object_url('node', self.node_name, 'nic', self.nic_name)
        q = self.s.delete(url)
        if q.ok:
            return
        elif q.status_code == 404:
            raise errors.NotFoundError(
                    "Nic not found. Nothing to delete."
                    )
        elif q.status_code == 409:
            raise errors.BlockedError(
                    "Cannot delete nic, diconnect it from network first"
                    )

    def connect_network(self, node, nic, network, channel):
        """ Connect <node> to <network> on given <nic> and <channel>"""

        self.node = node
        self.nic = nic
        self.network = network
        self.channel = channel

        url = self.object_url(
                'node', self.node, 'nic', self.nic, 'connect_network'
                )
        payload = json.dumps({
            'network': self.network, 'channel': self.channel
            })
        q = self.s.post(url, payload)
        if q.ok:
            return
        if q.status_code == 404:
            raise errors.NotFoundError(
                    "Resource or relationship does not exist. "
                    )
        if q.status_code == 409:
            raise errors.DuplicateError("A network is already attached.")
        if q.status_code == 412:
            raise errors.ProjectMismatchError(
                    "Project does not have access to either resource. "
                    )
        if q.status_code == 423:
            raise errors.BlockedError(
                    "Networking operations pending on this nic. "
                    )

    def detach_network(self, node, nic, network):
        """ Disconnect <node> from <network> on the given <nic>. """

        self.node = node
        self.nic = nic
        self.network = network

        url = self.object_url(
                'node', self.node, 'nic', self.nic, 'detach_network'
                )
        payload = json.dumps({'network': self.network})
        q = self.s.post(url, payload)
        if q.ok:
            return
        if q.status_code == 400:
            raise errors.NotFoundError(
                    "No such network attached to the nic. "
                    )
        if q.status_code == 423:
            raise errors.BlockedError(
                    "Networking operations pending on this nic. "
                    )

    def show_console(self, node):
        """ Display console log for <node> """
        pass

    def start_console(self, node):
        """ Start logging console output from <node> """
        self.node = node
        url = self.object_url('node', self.node, 'console')
        q = self.s.put(url)
        if q.ok:
            return

    def stop_console(self, node):
        """ Stop logging console output from <node> and delete the log"""
        self.node = node
        url = self.object_url('node', self.node, 'console')
        q = self.s.delete(url)
        if q.ok:
            return