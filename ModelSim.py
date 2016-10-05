from pubSubscr import *

class Model( Subscriber ):
   NEXT_IDENT = 0

   def __init__( self, ident=None ):
      self._sim     = None    # The simulation this inst is a part of (assigned in _addedToSimulation())
      self._ident   = ident   # The ID of this inst

      if ident is None:
         self._ident = Model.NEXT_IDENT
         Model.NEXT_IDENT += 1

   # Specialization of Subscriber
   def handleMessage( self, aMsg ):
      '''Message handler for published messages.'''
      raise NotImplementedError( )

   # Extension
   def ident( self ):
      return self._ident

   def subscriptionTopics( self ):
      '''Derived class must return a list of topics.'''
      raise NotImplementedError( )

   def _addedToSimulation( self, aSimulation ):
      '''Called after the model is added to a simulation.'''
      self._sim = aSimulation

   def _droppedFromSimulation( self, aSimulation ):
      '''Called before the model is dropped from a simulation.'''
      pass

   def postMessage( self, topic, **payload ):
      '''Convenience for posting messages.'''
      self._sim.postMessage( Message(topic, self, self._sim.simTime(), **payload) )

   # Interface called by Simulation Instance
   def tick( self ):
      '''Perform your primary processing.'''
      raise NotImplementedError( )


class Simulation( PostOffice ):
   def __init__( self ):
      PostOffice.__init__( self )
      self._models = [ ]   # list of Model instances currently in the simulation.
      self._tickFn = [ ]   # list of the tick methods of the models
      self._time   = 0     # current simulation time

   # Extension
   def add( self, aModel ):
      '''Add a model to the simulation.  Subscribe it to all topics
      returned it's subscriptionTopics() method.'''
      self._models.append( aModel )
      self._tickFn.append( aModel.tick )
      #self.subscribeTo( aModel, *aModel.subscriptionTopics() )
      #self.postMessage( Message('join', aModel, self._time) )
      aModel._addedToSimulation( self )

   def drop( self, aModel ):
      '''Remove a model from the simulation.  Unsubscribe it from all topics.'''
      aModel._droppedFromSimulation( self )
      #self.postMessage( Message('drop', aModel, self._time) )
      #self.unsubscribeFromAll( aModel )
      self._tickFn.remove( aModel.tick )
      self._models.remove( aModel )

   def reset( self ):
      self._models = [ ]
      self._tickFn = [ ]
      self._time   = 0

   def size( self ):
      '''Return the number of Models in the simulation.'''
      return len(self._models)

   def simTime( self ):
      '''Return the current simulation time (tick number).'''
      return self._time

   def __iter__( self ):
      return iter(self._models)

   def advanceSim( self, numTicks=1 ):
      '''Run the simulation for a specified number of ticks.'''
      for tickCount in range(numTicks):
         self.deliverAllPostedMessages( )
         for model in self._models:
            model.tick( )
         self._time += 1

   def tickAllModels_NoMessaging( self, numTicks):
      '''Tick all models (no message delivery, no exception handling).'''
      for t in range(self._time, self._time + numTicks):
         for tickFn in self._tickFn:
            tickFn( t )
      self._time += numTicks
   
   def tickAllModelsOnce_NoMessaging( self ):
      '''Tick all models once (no message delivery, no exception handling).'''
      for tickFn in self._tickFn:
         #try:
         tickFn( )
         #except:
            #pass
      self._time += 1


if __name__ == '__main__':
   gVal = 0
   
   class TestModel_A( Model ):
      def __init__( self ):
         super().__init__( self )
      
      def subscriptionTopics( self ):
         return [ ]
      
      def tick( self, t ):
         global gVal
         
         gVal += 1
      
   class TestModel_B( Model ):
      def __init__( self ):
         super().__init__( self )
      
      def subscriptionTopics( self ):
         return [ ]
      
      def tick( self, t ):
         global gVal
         
         print( gVal )
   
   SIM = Simulation( )
   SIM.add( TestModel_A() )
   SIM.add( TestModel_B() )
   
   def runSim( ):
      SIM.advanceSim(1000)
   
   def runSim2( ):
      for x in range(1000):
         SIM.tickAllModels( 1 )
   
   import timeit
   print( '==> ', timeit.timeit( 'runSim2()', setup='from __main__ import runSim2', number=100 ) )
   
   #import profile
   #profile.run( 'runSim3()' )
   
