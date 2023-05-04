#include <sys/ioctl.h>
#include <stdio.h>
#include <linux/rtc.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

int main()
{
    int fd; // Device file path
    int batteryStatus; // Status of battery 
    int retval = 0; // Return value of ioctl function (-1 = Error)

    // 1st step: Open Driver
    printf("\nOpening Driver\n");
    fd = open("/dev/rtc", O_RDONLY);

    // 2nd step: Display error in command line if the device
    // file wasn't found and close application
    if(fd < 0) {
        printf("Device file not found n\n");
        return 0;
    }


    // 3rd step: Read out 
    printf("Process ioctl access to read battery status\n");
    retval = ioctl(fd, RTC_VL_DATA_INVALID, &batteryStatus);

    if (retval == -1){
        // 4th step: Display error in command line if the ioctl function isn't able to access 
        // the specific function
        printf("Error access ioctl function \n");
        return 0; 
    } else {
        // 5th step: Print battery status
        printf("Battery status (1 = Error) %d\n", batteryStatus);
    }
        // Close driver
        printf("Closing Driver\n");
        close(fd);
} // main
