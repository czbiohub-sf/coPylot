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

