#include <unistd.h>
#include <signal.h>
#include "blackstar.h"

static void *footswitch_data_push(void *vargp);
static void *footswitch_data_pull(void *vargp);
static void *footswitch_evt_handler(void *vargp);
static void handle_sigint(int sig);

int main(int argc, char* argv[])
{
    blackstar_err_t res;
    
    signal(SIGINT, handle_sigint);
    signal(SIGTERM, handle_sigint);

    res = blackstar_init(BLACKSTAR_INSTANCE);

    pthread_attr_init(&footswitch_push_thread_attr); 
    pthread_create(&footswitch_push_thread,
                   &footswitch_push_thread_attr,
                   footswitch_data_push,
                   &shared_resources);

    pthread_attr_init(&footswitch_pull_thread_attr); 
    pthread_create(&footswitch_pull_thread,
                   &footswitch_pull_thread_attr,
                   footswitch_data_pull,
                   &shared_resources);

    pthread_attr_init(&footswitch_evt_thread_attr); 
    pthread_create(&footswitch_evt_thread,
                   &footswitch_evt_thread_attr,
                   footswitch_evt_handler,
                   &shared_resources);
    
    pthread_join(footswitch_evt_thread , NULL);
    pthread_join(footswitch_push_thread, NULL);
    pthread_join(footswitch_pull_thread, NULL);

    blackstar_deinit(BLACKSTAR_INSTANCE);
    return 0;
}

void handle_sigint(int sig)
{
    shared_resources.thread_alive = 0;
}

void *footswitch_data_push(void *vargp)
{
    pthread_shared_t *shared_resources = (pthread_shared_t *) vargp;
    while (shared_resources->thread_alive == 1)
    {
        printf("In footswitch_data_push\n");
        sleep(1);
    }
}

void *footswitch_data_pull(void *vargp)
{
    pthread_shared_t *shared_resources = (pthread_shared_t *) vargp;
    while (shared_resources->thread_alive == 1)
    {
        printf("In footswitch_data_pull\n");
        sleep(1);
    }
}

void *footswitch_evt_handler(void *vargp)
{
    pthread_shared_t *shared_resources = (pthread_shared_t *) vargp;
    while (shared_resources->thread_alive == 1)
    {
        printf("In footswitch_evt_handler\n");
        sleep(1);
    }
}