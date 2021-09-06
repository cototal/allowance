<?php

namespace App\Service;

use App\Entity\Entry;
use App\Entity\Task;
use Doctrine\ORM\EntityManagerInterface;

class TaskService
{
    /**
     * @var EntityManagerInterface
     */
    private $em;

    public function __construct(EntityManagerInterface $em)
    {
        $this->em = $em;
    }

    /**
     * @param Task $task
     * @return Entry|null
     */
    public function payUp(Task $task)
    {
        if (count($task->getDays()) <= 3) {
            $task->setDays([]);
            $this->em->flush();
            return null;
        }
        $price = round(count($task->getDays()) / 7.0, 2) * -10;
        $entry = (new Entry())
            ->setUser($task->getUser())
            ->setEntryDate(new \DateTimeImmutable())
            ->setPayee($task->getUser()->getUsername())
            ->setPrice($price)
            ->setCategory("Allowance Task");
        $this->em->persist($entry);
        $task->setDays([]);
        $this->em->flush();
        return $entry;
    }
}