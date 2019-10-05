#include "contiki.h"

#include <stdio.h>

/*---------------------------------------------------------------------------*/
PROCESS(fubar_process, "Hello world process");
AUTOSTART_PROCESSES(&fubar_process);
/*---------------------------------------------------------------------------*/
PROCESS_THREAD(fubar_process, ev, data)
{
  PROCESS_BEGIN();

  printf("Hello, world\n");
  
  PROCESS_END();
}
/*---------------------------------------------------------------------------*/
