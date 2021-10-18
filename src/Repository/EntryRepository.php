<?php

namespace App\Repository;

use App\Entity\Entry;
use App\Entity\User;
use App\Utils\GeneralUtils;
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

    public function searchQuery(?array $query)
    {
        $qb = $this->createQueryBuilder("entry")
            ->join("entry.user", "user")
            ->addSelect("user");

        if (empty($query)) {
            return $qb;
        }

        if (!GeneralUtils::emptyKeyValue("userEquals", $query)) {
            $qb->andWhere("user.id = :userId")
                ->setParameter("userId", $query["userEquals"]);
        }

        foreach (["category", "payee", "notes"] as $field) {
            $value = '%' . $query["${field}Contains"] . '%';
            if (!GeneralUtils::emptyKeyValue("${field}Contains", $query)) {
                $qb->andWhere("entry.$field LIKE :$field")
                    ->setParameter($field, $value);
            }
        }

        if (!GeneralUtils::emptyKeyValue("dateFrom", $query)) {
            $qb->andWhere("entry.entryDate >= :dateFrom")
                ->setParameter("dateFrom", $query["dateFrom"]);
        }

        if (!GeneralUtils::emptyKeyValue("dateTo", $query)) {
            $qb->andWhere("entry.entryDate <= :dateTo")
                ->setParameter("dateTo", $query["dateTo"]);
        }

        return $qb;
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
            ->andWhere("entry.price > 0")
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
