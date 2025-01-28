<?php

namespace App\Controller;

use App\Entity\Entry;
use App\Entity\Task;
use App\Entity\User;
use App\Form\EntrySearchType;
use App\Form\EntryType;
use Doctrine\ORM\EntityManagerInterface;
use Knp\Component\Pager\PaginatorInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route("/entry")]
class EntryController extends AbstractController
{
    private ?EntityManagerInterface $em;
    private ?PaginatorInterface $paginator;

    public function __construct(EntityManagerInterface $em, PaginatorInterface $paginator)
    {
        $this->em = $em;
        $this->paginator = $paginator;
    }

    #[Route("", name: "entry_index", methods: ["GET"])]
    public function index(Request $request): Response
    {
        $searchParams = $request->query->all("entry_search");
        $searchPrefill = $this->searchPrefill($searchParams);
        $query = $this->em->getRepository(Entry::class)
            ->searchQuery($searchParams);
            // ->createQueryBuilder("entry")
            // ->join("entry.user", "user");
        $pagination = $this->paginator->paginate($query, $request->query->getInt("page", 1), 30, [
            "defaultSortFieldName" => "entry.entryDate",
            "defaultSortDirection" => "DESC"
        ]);
        $searchForm = $this->createForm(EntrySearchType::class, $searchPrefill, [
            "method" => "GET"
        ]);
        $balance = $this->em->getRepository(Entry::class)->balance($this->getUser());
        $monthlySpending = $this->em->getRepository(Entry::class)->monthlySpending($this->getUser(), new \DateTime());
        $monthlySpending = max([$monthlySpending, 0]);
        $task = $this->em->getRepository(Task::class)->findOneBy(["user" => $this->getUser()]);
        return $this->render('entry/index.html.twig', [
            'pagination' => $pagination,
            "searchForm" => $searchForm->createView(),
            "balance" => $balance,
            "monthlySpending" => $monthlySpending,
            "task" => $task
        ]);
    }

    #[Route("/new", name: "entry_new", methods: ["GET", "POST"])]
    public function new(Request $request): Response
    {
        $entry = new Entry();
        $form = $this->createForm(EntryType::class, $entry);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $entry->setUser($this->getUser());
            $this->em->persist($entry);
            $this->em->flush();

            return $this->redirectToRoute("entry_show", ["id" => $entry->getId()]);
        }

        return $this->render('entry/new.html.twig', [
            'entry' => $entry,
            'form' => $form->createView(),
        ]);
    }

    #[Route("/{id}", name: "entry_show", methods: ["GET"])]
    public function show(Entry $entry): Response
    {
        return $this->render('entry/show.html.twig', [
            "entry" => $entry,
        ]);
    }

    #[Route("/{id}/edit", name: "entry_edit", methods: ["GET", "POST"])]
    public function edit(Request $request, Entry $entry): Response
    {
        $form = $this->createForm(EntryType::class, $entry);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $this->em->flush();

            return $this->redirectToRoute('entry_index', [], Response::HTTP_SEE_OTHER);
        }

        return $this->render('entry/edit.html.twig', [
            'entry' => $entry,
            'form' => $form->createView(),
        ]);
    }

    #[Route("/{id}", name: "entry_delete", methods: ["DELETE"])]
    public function delete(Request $request, Entry $entry): Response
    {
        if ($this->isCsrfTokenValid("delete" . $entry->getId(), $request->query->get("_token"))) {
            $this->em->remove($entry);
            $this->em->flush();
        }

        return $this->json(null, 204);
    }

    private function searchPrefill($searchParams): array
    {
        if (empty($searchParams)) {
            return [];
        }
        $output = [];
        foreach ($searchParams as $key => $value) {
            if (empty($value)) {
                continue;
            }
            switch($key) {
                case "userEquals":
                    $output["userEquals"] = $this->em->getRepository(User::class)->find($value);
                    break;
                case "dateFrom":
                case "dateTo":
                    $output[$key] = \DateTimeImmutable::createFromFormat("Y-m-d", $value);
                    break;
                default:
                    $output[$key] = $value;
            }
        }
        return $output;
    }
}
