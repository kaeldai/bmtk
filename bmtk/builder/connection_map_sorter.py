import numpy as np
import heapq

from .builder_utils import mpi_rank, mpi_size


def cm_key(cm):
    return cm.max_connections()


def basic_rank_split(connection_maps):
    return connection_maps[mpi_rank::mpi_size]


def sort_cms(connection_maps):
    connection_maps.sort(reverse=True, key=cm_key)
    return connection_maps


def sort_cm_on_rank(connection_maps):
    connection_maps.sort(reverse=True, key=cm_key)
    rank_tallys = []
    for _ in range(mpi_size):
        heapq.heappush(rank_tallys, (0, []))
    
    for cm in connection_maps:
        edge_count, rank_cms = heapq.heappop(rank_tallys)
        rank_cms.append(cm)
        edge_count += cm.max_connections()
        heapq.heappush(rank_tallys, (edge_count, rank_cms))

    return rank_tallys[mpi_rank][1]

    # print([f'{c[0]:,}' for c in rank_tallys])
    # for r in range(mpi_size):
    #     print(r, len(rank_tallys[r][1]))

    # for r in range(mpi_size):
    #     print(r, [r.max_connections() for r in rank_tallys[r][1]])


def order_connection_maps(connection_maps):
    if mpi_size == 0:
        return sort_cms(connection_maps)
    else:
        return sort_cm_on_rank(connection_maps)
