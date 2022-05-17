Hardware
------------------

coPylot implements device adapters on top of the vendor provided
drivers, APIs and SDKs as well as on top of the drivers and lower
level APIs we developed. Within these adapters, coPylot also has
many convenience methods. To enable developers/experimentalists
who might want to use the same functionalities here we are
sharing our hardware API:


ASIStage
    .. currentmodule:: copylot.hardware.asi_stage.stage

    .. autosummary::
        ASIStage


FilterWheel
    .. currentmodule:: copylot.hardware.filterwheel.filterwheel

    .. autosummary::
        FilterWheel

NIDaq
    .. currentmodule:: copylot.hardware.ni_daq.nidaq

    .. autosummary::
        NIDaq

.. OrcaCamera
    .. currentmodule:: copylot.hardware.orca_camera.camera

..     .. autosummary::
        OrcaCamera

WaterDispenserControl
    .. currentmodule:: copylot.hardware.water_dispenser.water_dispenser_control

    .. autosummary::
        WaterDispenserControl


ASI Stage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: copylot.hardware.asi_stage.stage

.. autoclass:: ASIStage
    :members:
    :inherited-members:


FilterWheel
~~~~~~~~~~~~~~~~~

.. currentmodule:: copylot.hardware.filterwheel.filterwheel

.. autoclass:: FilterWheel
    :members:
    :inherited-members:


NIDaq
~~~~~~~~~~~~~~~~~

.. currentmodule:: copylot.hardware.ni_daq.nidaq

.. autoclass:: NIDaq
    :members:
    :inherited-members:


.. OrcaCamera
 ~~~~~~~~~~~~~~

.. .. currentmodule:: copylot.hardware.orca_camera.camera

.. .. autoclass:: OrcaCamera
    :members:
    :inherited-members:


WaterDispenserControl
~~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: copylot.hardware.water_dispenser.water_dispenser_control

.. autoclass:: WaterDispenserControl
    :members:
    :inherited-members:
