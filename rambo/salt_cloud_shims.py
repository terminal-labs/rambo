def vb_import_ovf(name=None):
    """
    Import an OVF and use it to create a machine on the virtualbox hypervisor
    """
    vbox = vb_get_box()
    log.info("Import virtualbox ovf machine %s ", name)
    new_machine = vbox.createAppliance()
    new_machine.read("/home/chris/Desktop/box/box.ovf")
    new_machine.interpret()
    new_machine.importMachines([])
    log.info("Finished creating %s", name)
    return vb_xpcom_to_attribute_dict(new_machine, "IMachine")
