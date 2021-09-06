<?php

namespace App\Command;

use App\Entity\Entry;
use App\Entity\Task;
use App\Entity\User;
use App\Service\TaskService;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputArgument;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Input\InputOption;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Console\Style\SymfonyStyle;

class TaskCommand extends Command
{
    protected static $defaultName = 'app:task';
    protected static $defaultDescription = 'Add a short description for your command';

    /**
     * @var EntityManagerInterface
     */
    private $em;
    /**
     * @var TaskService
     */
    private $taskService;

    public function __construct(EntityManagerInterface $em, TaskService $taskService)
    {
        $this->em = $em;
        parent::__construct();
        $this->taskService = $taskService;
    }

    protected function configure(): void
    {
        $this
            ->setDescription(self::$defaultDescription)
        ;
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $io = new SymfonyStyle($input, $output);
        $tasks = $this->em->getRepository(Task::class)->findAll();
        $count = 0;
        foreach ($tasks as $task) {
            $entry = $this->taskService->payOut($task);
            if (!empty($entry)) {
                ++$count;
            }
        }
        $this->em->flush();
        $io->success("Allowance task paid out to $count users");

        return 0;
    }
}
