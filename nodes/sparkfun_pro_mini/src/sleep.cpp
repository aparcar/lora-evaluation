#include <LowPower.h>

void sleep_minutes(unsigned minutes)
{
    for (unsigned i = 0; i < minutes; i++)
    {
        for (unsigned j = 0; j < 7; j++)
        {
            LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
        }
        LowPower.powerDown(SLEEP_2S, ADC_OFF, BOD_OFF);
        LowPower.powerDown(SLEEP_2S, ADC_OFF, BOD_OFF);
    }
}