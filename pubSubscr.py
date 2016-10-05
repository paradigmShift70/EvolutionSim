class Message( object ):
   NEXT_SERIAL_NO = 0
   def __init__( self, topic, sender, time, **payload ):
      self.serialNo = Message.NEXT_SERIAL_NO
      self.time     = time

      self.topic    = topic
      self.sender   = sender
      self.payload  = payload

      Message.NEXT_SERIAL_NO += 1

   def __getitem__( self, key ):
      return self.payload[ key ]

   def __str__( self ):
      result = '[{0:05}] {1:05} - {2:10}: sender=\'{3}\''.format(
                   self.time, self.serialNo, self.topic, self.sender.ident())
      
      for key,val in self.payload.items():
         result += '; {0}={1}'.format(key, val)

      return result

class Subscriber( object ):
   # Interface
   def handleMessage( self, aMsg ):
      '''Message handler for published messages.'''
      raise NotImplementedError( )


class PostOffice( object ):
   def __init__( self ):
      self._subscriptions  = { '*':[ ] }  # Map: topic -> list of Subscriber instances
      self._postedMessages = [ ]          # Messages not yet delivered

   # Extension
   def subscribeTo( self, aSubscriber, *topics ):
      '''Register a Subscriber to one or more topics.'''
      if '*' in topics:
         self._subscriptions[ '*' ].append( aSubscriber )
         for topic in self._subscriptions.values():
            topic.append( aSubscriber )
      else:
         for topic in topics:
            try:
               self._subscriptions[topic].append( aSubscriber )
            except:
               self._subscriptions[topic] = [ aSubscriber ] + self._subscriptions[ '*' ]

   def unsubscribeFrom( self, aSubscriber, *topics ):
      '''Unregister a Subscriber from one or more topics.'''
      for topic in topics:
         try:
            subscrList = self._subscriptionLists[ aTopic ]
            subscrList.remove( aSubscriber )

            if len(subscrList) == 0:
               del self._subscriptionLists[ aTopic ]
         except:
            pass

   def unsubscribeFromAll( self, aSubscriber ):
      '''Remove all a Subscriber from all subscriptions.'''
      self.unsubscribeFrom( aSubscriber, *self._subscriptions.keys( ) )

   def postMessage( self, aMsg ):
      '''Post a message to the message queue.  Delivery will occur in
      batch when deliverAllPostedMessages( ) is called.'''
      self._postedMessages.append( aMsg )

   def deliverMessage( self, aMsg ):
      '''Deliver aMsg to all subscribers of aMsg.topic.'''
      try:
         for subscriber in self._subscriptions[aMsg.topic]:
            try:
               subscriber.handleMessage( aMsg )
            except:
               self.postMessage( Message('ERROR', subscriber, '?', msg='Unable to handle message', detail=aMsg) )
      except:
         pass

   def deliverAllPostedMessages( self ):
      '''Deliver all posted messages.'''
      for msg in self._postedMessages:
         self.deliverMessage( msg )
      
      self._postedMessages.clear( )

