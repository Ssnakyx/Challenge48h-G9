<?php

namespace App\Form;

use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\DateTimeType;
use Symfony\Component\Form\Extension\Core\Type\NumberType;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use Symfony\Component\Form\FormBuilderInterface;

class MapFilterType extends AbstractType
{
    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
            ->add('dateMin', DateTimeType::class, [
                'label' => 'Date minimum',
                'widget' => 'single_text',
                'required' => false,
            ])
            ->add('dateMax', DateTimeType::class, [
                'label' => 'Date maximum',
                'widget' => 'single_text',
                'required' => false,
            ])
            ->add('indexMin', NumberType::class, [
                'label' => 'Score minimum',
                'widget' => 'single_text',
                'required' => false,
            ])
            ->add('indexMax', NumberType::class, [
                'label' => 'Score maximum',
                'widget' => 'single_text',
                'required' => false,
            ])
            ->add('searchArea', TextType::class, [
                'label' => 'Zone de recherche ',
                'widget' => 'single_text',
                'required' => false,
            ])
        ;
    }
}
