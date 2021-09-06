<?php

namespace App\Repository;

use App\Entity\Entry;
use App\Entity\User;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @method Entry|null find($id, $lockMode = null, $lockVersion = null)
 * @method Entry|null findOneBy(array $criteria, array $orderBy = null)
 * @method Entry[]    findAll()
 * @method Entry[]    findBy(array $criteria, array $orderBy = null, $limit = null, $offset = null)
 */
class EntryRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, Entry::class);
    }

    public function balance(User $user)
    {
        $total = $this->createQueryBuilder("entry")
            ->select("SUM(entry.price)")
            ->andWhere("entry.user = :user")
            ->setParameter("user", $user)
            ->getQuery()
            ->getSingleScalarResult();
        if (is_null($total)) {
            return 0;
        }
        return -floatval($total);
    }

    public function monthlySpending(User $user, \DateTimeInterface $date)
    {
        $firstString = $date->format("Y-m-01 00:00");
        // 't' gets the number of days in a month
        $lastString = $date->format("Y-m-t 23:59");
        $first = \DateTimeImmutable::createFromFormat("Y-m-d H:i", $firstString);
        $last = \DateTimeImmutable::createFromFormat("Y-m-d H:i", $lastString);
        $total = $this->createQueryBuilder("entry")
            ->select("SUM(entry.price)")
            ->andWhere("entry.user = :user")
            ->andWhere("entry.entryDate >= :first AND entry.entryDate <= :last")
            ->setParameter("user", $user)
            ->setParameter("first", $first)
            ->setParameter("last", $last)
            ->getQuery()
            ->getSingleScalarResult();
        if (is_null($total)) {
            return 0;
        }
        return floatval($total);
    }
}
