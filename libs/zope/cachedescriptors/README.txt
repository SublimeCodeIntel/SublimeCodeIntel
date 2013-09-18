==================
Cached descriptors
==================

Cached descriptors cache their output.  They take into account
instance attributes that they depend on, so when the instance
attributes change, the descriptors will change the values they
return.

Cached descriptors cache their data in _v_ attributes, so they are
also useful for managing the computation of volatile attributes for
persistent objects.

Persistent descriptors:

  property

     A simple computed property. See property.txt.

  method

     Idempotent method.  The return values are cached based on method
     arguments and on any instance attributes that the methods are
     defined to depend on.

     **Note**, only a cache based on arguments has been implemented so far.
     
     See method.txt.
